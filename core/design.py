from datetime import datetime,timedelta

import utils
import db
import re

class Time:
     # verifier tous les formats...
    def __init__(self,str_time):
        str_time = utils.cleanup(str_time)
        hms=re.findall('\d+',str_time)
        while len(hms)<3:
            hms.insert(0,'0')
        hms=list(map(lambda x: int(x),hms))

        self.time = timedelta(hours=hms[0],minutes=hms[1],seconds=hms[2])

    def __str__(self):
            s=self.time.total_seconds()
            if int(s//3600) == 0:
                return "{}'{}''".format(int(s % 3600 // 60),int(s % 60))
            else:
                return "{:02}h{}'{}''".format(int(s//3600),int(s % 3600 //60),int(s % 60))

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
    def __init__(self, ID, racetype):
        self.ID = ID
        self.racetype = racetype
        self.name =''
        self.results = []
        self.pullDB() #pull results either from FFA DB or internal
        # ID => string
        # racetype => string
        # results => [{'errcode':,'rstl':rank,time,name,ID,club,cat,gender}]

    def pullDB(self):
        if db.check_race_exists(self): #RaceDB:
            print('This race is being processed from internal database...')
            db.raceDB_to_race(self)
            # assign values to attributes
        else:
            print('This race is being processed from FFA database...')
            self.name, self.results=self.pullFFA()#a homogeneiser avec runner.pullFFA 
                    # ne pas affecter de variable
            self.pushDB()

    def pullFFA(self):
        # put urlFFA inside extract_resultlines
        urlFFA ='http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition='+self.ID+'&frmepreuve='+self.racetype
        race_name,results = utils.extract_race(urlFFA)
        return race_name,results

    def pushDB(self):
        db.race_to_raceDB(self)

    def extract_runners_from_race(self):
        for rl in self.results:
            #if rl['rstl'][3] != '':
                _runner = Runner(rl['rstl'][3],rl['rstl'][2],rl['rstl'][5],rl['rstl'][6],rl['rstl'][4])
                yield _runner

    def show(self):
        print('Race ID: {} Race type: {}\n'.format(self.ID,self.racetype))
        for rl in self.results:
            _t=tuple(rl['rstl'])+(rl['errcode'],)
            print('#{} Time:{} Name:{} Runner ID:{} Club:{} Category:{} Gender:{} ErrorCode:{}'.format(*_t))

    def write_to_csv(self,path,filename):
        with open(path + '/' + filename + '.csv', 'w',encoding='utf8') as f:
            f.write("class;temps;nom;cat;sexe;club\n")
            for r in self.results:
                rw=r['rstl'][:] #shallow copy to preserve results
                rw.pop(3)
                f.write(';'.join(map(lambda x: str(x),rw))+'\n')
        f.close()
        return 'race_files/' + filename + '.csv'

    def flatten_results(self):
        result_lines = [r['rstl'] for r in self.results]
        errcodes = [r['errcode'] for r in self.results]
        return result_lines,errcode

if __name__ == '__main__':
    race_1 = Race('184050','30+Km')
    tab_records = []
    for i,r_ in enumerate(race_1.extract_runners_from_race()):
        print(r_.name,list(r_.list_records(10)))

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
