from datetime import datetime,timedelta
import urllib.parse
import utils
import db
import re
import statistics as stat

class TimeNew:
    def __init__(self,tmdelta):
        self.time = tmdelta

    def __str__(self):
            s=self.time.total_seconds()
            if int(s//3600) == 0:
                return "{}'{}''".format(int(s % 3600 // 60),int(s % 60))
            else:
                return "{:02}h{}'{}''".format(int(s//3600),int(s % 3600 //60),int(s % 60))

    @classmethod
    def time_from_string(cls,str_time):
        hms = utils.str_to_hms(str_time)
        tmdelta = timedelta(hours=hms[0],minutes=hms[1],seconds=hms[2])
        return cls(tmdelta)

    @classmethod
    def time_from_timedelta(cls,tmdelta):
        return cls(tmdelta)

    @classmethod
    def time_from_hms(cls,hms):
        tmdelta = timedelta(hours=hms[0],minutes=hms[1],seconds=hms[2])
        return cls(tmdelta)

    @classmethod
    def time_from_seconds(cls,total_seconds):
        tmdelta = timedelta(hours=int(total_seconds//3600),minutes=int(total_seconds % 3600 // 60), seconds = int(total_seconds % 60))
        return cls(tmdelta)

class Runner:
    def __init__(self,ID,name,category,gender,club):
        self.ID = ID
        self.name = name
        self.category = category
        self.gender = gender
        self.club = club
        self.records= {}
        if ID:
            self.pullDB() #pull results either from FFA DB or internal

    def __str__(self):
        return 'ID: ' + self.ID + ' ' + ' Name: ' + self.name + ' Cat: '+ self.category + ' Gender: ' + self.gender + ' Club: ' + self.club

    def pullDB(self):
        if db.check_runner_exists(self):
            print('This runner is being processed from internal database...')
            #update records in DB
            db.runnerDB_to_runner(self)
        else:
            print('This runner is being processed from FFA database...')
            self.records=self.pullFFA()
            self.pushDB()
            #self.pullDB()#to retrieve correct timedelta...TODO: convert timedelta into time object

    def pushDB(self):
        db.runner_to_runnerDB(self)

    def pullFFA(self):
        return utils.correct_records(utils.extract_records(self))

    def year_record(self,race_type,year):
        """returns record of year for racetype, if record does not exists raise an
        error
        """
        return self.records[utils.dateracetype_to_DBcolumn(year,str(race_type))]


    def list_records(self,race_type):
        """yield records value (if it exists) for a race_type (10,15,21 or 42)k
        """
        yearnow = datetime.now().year
        yearlist = range(yearnow,yearnow-4,-1)
        for y in yearlist:
            try:
                yield self.year_record(race_type,y)
            except KeyError:
                yield None

class Race:
    """ Class Race
    Results are extracted either from FFA site or from internal database
    race.results=[{'errcode':,'rstl':[rank,time(TimeNew
    Object),name,ID,club,cat,gender,racetype_human]},...]
    """
    def __init__(self, ID, racetype):
        self.ID = ID #string
        self.racetype = racetype #string
        self.racetype_human = urllib.parse.unquote(self.racetype).replace('+',' ')
        self.name = ''
        self.date = ''
        self.results = []
        self.race_stats = {}
        self.pullDB() #pull results either from FFA DB or internal
        self.name = self.name.lower().title() # prettify the name once retrieved
        # results => [{'errcode':,'rstl':rank,time(TimeNew # object),name,ID,club,cat,gender,racetype_human}]

    def pullDB(self):
        if db.check_race_exists(self): #RaceDB:
            print('This race is being processed from internal database...')
            db.raceDB_to_race(self)
            # assign values to attributes
        else:
            print('This race is being processed from FFA database...')
            self.name, self.results=self.pullFFA()#a homogeneiser avec runner.pullFFA 
            #xtraire la date du nom
            self.date = self.name.split(' - ')[0]
            self.name = self.name.split(' - ')[1]
            self.pushDB()
            #self.pullDB() #to retrieve correct timedelta...TODO: convert timedelta into time object

    def pullFFA(self):
        # put urlFFA inside extract_resultlines
        urlFFA ='http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition='+self.ID+'&frmepreuve='+self.racetype
        race_name,results = utils.extract_race(urlFFA)
        return race_name,results

    def pushDB(self):
        db.race_to_raceDB(self)

    def resetDB(self):
        #TODO: allow user to reset all the race datas
        db.delete_race(self)
        self.pullDB()

    def extract_runners_from_race(self):
        for rl in self.results:
                _runner = Runner(rl['rstl'][3],rl['rstl'][2],rl['rstl'][5],rl['rstl'][6],rl['rstl'][4])
                yield _runner

    def show(self):
        print('Race ID: {} Race type: {} Race date: {} Race name: {}\n'.format(self.ID,self.racetype,self.date,self.name))
        for rl in self.results:
            _t=tuple(rl['rstl'])+(rl['errcode'],)
            print('#{} Time:{} Name:{} Runner ID:{} Club:{} Category:{} Gender:{} ErrorCode:{}'.format(*_t))

    def write_to_csv(self,path,filename):
        with open(path + '/' + filename + '.csv', 'w',encoding='ISO_8859-1') as f:
            f.write("class;temps;nom;cat;sexe;club\n")
            for r in self.results:
                rw=r['rstl'][:] #shallow copy to preserve results
                rw.pop(3)
                rw.append(rw.pop(3))
                f.write(';'.join(map(lambda x: str(x),rw))+'\n')
        f.close()
        return 'race_files/' + filename + '.csv'

    def flatten_results(self):
        result_lines = [r['rstl'] for r in self.results]
        errcodes = [r['errcode'] for r in self.results]
        return result_lines,errcode

    def create_race_stats(self,stat_value='meantime',sample_size=None):
        if sample_size is None:
            sample_size = len(self.results)
            postfix = ''
        else:
            postfix = '_' + str(sample_size)

        timelist = [t['rstl'][1].time.total_seconds() for t in self.results[:sample_size]]

        if stat_value == 'meantime':
            meantime = TimeNew.time_from_seconds(stat.mean(timelist))
            self.race_stats['meantime' + postfix] = meantime
        elif stat_value == 'mediantime':
            mediantime = TimeNew.time_from_seconds(stat.median(timelist))
            self.race_stats['mediantime' + postfix] = mediantime

        print(self.race_stats)

class RaceCollection:
    def __init__(self, race_list = []):
        self.race_list = []
        if not race_list:
            self.collect_racesDB()
        else:
            self.race_list = [ Race(race_ID,race_type) for race_ID,race_type in
                              race_list ]
        self.main_stats = {'runner_nb': len(self.race_list)}

    def collect_racesDB(self):
        self.race_list = [ Race(race[0],race[1]) for race in db.collect_races()]

    def show(self):
        print('Runner number: {}'.format(self.main_stats['runner_nb']))
        for race in self.race_list:
            print('Race ID: {} Race type: {} Race date: {} Race name: {} '.format(race.ID,race.racetype,race.date,race.name))

    def update_races(self):
        """ if new column is created in the DB, all races can be updated thanks
        to this function """
        # update names and dates (to be commented)
        for race in self.race_list:
            if race.date == None:
                print(race.date)
                race.date = race.name.split(' - ')[0]
                race.name = race.name.split(' - ')[1]
            race.pushDB()

if __name__ == '__main__':

    race_list = [('225157', '15+km'), ('223631', '22+km')]
    race_collection = RaceCollection()
    race_collection.show()



#    race_collection = RaceCollection()
#    db.reset_races()
#    race_collection.update_races()
#    race_collection.collect_racesDB()
#    race_collection.show()


##    race_1 = Race('209915','10+km')
#    race_1.resetDB()
#    race_1.show()
    #db.delete_race(race_1)
#    for i in race_1.results:
#        print(i['rstl'][1])
#    print(race_1.results)
    #race_1.create_race_stats(10)
#    time_2 = TimeNew.time_from_string("30'45\"")
#    print(time_2)
#    tab_records = []
#    for i,r_ in enumerate(race_1.extract_runners_from_race()):
#        print(r_.name+':')
#        print(r_.list_records(10))
#        for t in r_.list_records(10):
#            print(t)

#    print(tab_records)


#    race_1.write_to_csv(root_path + project_path + static_path + '/race_files',race_1.ID + '_' + race_1.racetype)
#    print(race_1.name)
#    race_1.show()
#    race_2 = Race('205515','10+Km+Route')
#    race_2.write_to_csv('/home/ftg/python/ffablob/core/','race_'+race_2.ID+'_rt_'+race_2.racetype)
#    runner=Runner('528136','unknown','XX','X','DDDD')
#    print(runner.records)
#    utils.extract_records(runner)
#    for i in runner.records:
#        print(i['racetype']+'kms en '+i['annee']+': '+str(i['temps']))
