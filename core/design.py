from datetime import datetime,timedelta

import utils
import db

class Time:
     # verifier tous les formats...
    def __init__(self,str_time):
        str_time = utils.cleanup(str_time)
        try:
            dt = datetime.strptime(str_time,"%Hh%M'%S''")
        except ValueError:
            try:
                dt = datetime.strptime('00h' + str_time,"%Hh%M'%S''")
            except ValueError:
                try:
                    dt = datetime.strptime('00h' + str_time,"%Hh%M:%S''")
                except ValueError:
                    dt = datetime.strptime(str_time,"%H:%M:%S")

        self.time = timedelta(hours=dt.hour,minutes=dt.minute,seconds=dt.second)

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
        self.records=[]
        # Name => string
        # ID (not mandatory) => string
        # Birth date => date
        # Category => string
        # Gender => string
        # Club => string
        # Records => [{'year':,'time':}]

    def __str__(self):
        return 'ID: ' + self.ID + ' ' + ' Name: ' + self.name + ' Cat: '+ self.category + ' Gender: ' + self.gender + ' Club: ' + self.club

    def pullDB(self):
        if self.ID in RunnerDB:
        # gives values to attributes
            pass
        else:
            self.pullFFA()
        return _records

    def pushDB(self):
        pass

    def pullFFA(self):
        pass

    def populate_attrs(self,result_line):
        pass

class Race:
    def __init__(self, ID, racetype):
        self.ID = ID
        self.racetype = racetype
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
            self.results=self.pullFFA()
            self.pushDB()

    def pullFFA(self):
        urlFFA ='http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition='+self.ID+'&frmepreuve='+self.racetype
        results=utils.correct_resultlines(utils.extract_resultlines(urlFFA))
        return results

    def pushDB(self):
        db.race_to_raceDB(self)

    def show(self):
        print('Race ID: {} Race type: {}\n'.format(self.ID,self.racetype))
        for rl in self.results:
            _t=tuple(rl['rstl'])+(rl['errcode'],)
            print('#{} Time:{} Name:{} Runner ID:{} Club:{} Category:{} Gender:{} ErrorCode:{}'.format(*_t))

    def write_to_csv(self,path,filename):
        with open(path + filename + '.csv', 'w',encoding='utf8') as f:
            f.write("class;temps;nom;cat;sexe;club\n")
            for r in race_2.results:
                rw=r['rstl'][:].pop(3) #shallow copy to preserve results
                f.write(';'.join(map(lambda x: str(x),rw))+'\n')
        f.close()


if __name__ == '__main__':
    race_1 = Race('184050','30+Km')
    race_2 = Race('205515','10+Km+Route')
#    race_2.write_to_csv('/home/ftg/python/ffablob/core/','race_'+race_2.ID+'_rt_'+race_2.racetype)

