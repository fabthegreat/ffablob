import utils

class Runner:
    def __init__(self,ID,name,category,gender,club):
        self.ID = ID
        self.name = name
        self.category = category
        self.gender = gender
        self.club = club
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

class Time:
    def __init__(self): 
        pass

class Race:
    def __init__(self, ID, racetype):
        self.ID = ID
        self.racetype = racetype
        self.results = self.pullDB()

        # ID => string
        # racetype => string
        # results => [{'rank':,'time':,'runner':}]

    def pullDB(self):
        if self.ID in []: #RaceDB:
            # assign values to attributes
            pass
        else:
            return self.pullFFA()

    def pushDB(self):
        pass

    def pullFFA(self):
        urlFFA ='http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition='+self.ID+'&frmepreuve='+self.racetype
        utils.correct_resultlines(utils.extract_resultlines(urlFFA))

if __name__ == '__main__':
    race = Race('184050','30+Km')
