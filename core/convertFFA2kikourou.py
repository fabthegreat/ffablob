from bs4 import BeautifulSoup
import re
import urllib.request
import random
from datetime import datetime,timedelta
import sys

import bd

def time_converter(time):
    pass

def strtohex(js_ID): # to retrieve runner_ID from javascript input
    hexreturn = ""
    for i in range(1,len(str(js_ID))+1):
        hexreturn += str(99 - ord(str(js_ID)[i - 1]))
        hexreturn += str(ord(str(js_ID)[i - 1]))
    return hexreturn

def extract_soup(url):
        headers = { 'User-Agent' : 'Mozilla/5.0' }
        req = urllib.request.Request(url, None, headers)
        html = urllib.request.urlopen(req)
        soup = BeautifulSoup(html,"lxml") # parse html page with lxml and bs
        return soup

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def check_ranks(rankinf,ranksup):
    checkout=True
    if RepresentsInt(rankinf) and RepresentsInt(ranksup):
        rankinf,ranksup = int(rankinf),int(ranksup)
        return (checkout,rankinf,ranksup)
    else:
        checkout=False
        return (checkout,0,0)
    if rankinf>ranksup:
        checkout = False
        return (checkout,0,0)
    if rankinf<0 or ranksup<0:
        checkout = False
        return (checkout,0,0)

def check_url(url):
    valid=re.compile(r"^(http://bases.athle.com/asp.net/liste.aspx\?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=[0-9]*&frmepreuve=)")
    return bool(valid.match(url))

def cleanup(str_chrono):
        str_chrono = str_chrono.split("''")[0].strip()+"''"
        return str_chrono

class Chrono:
    # verifier tous les formats...
    def __init__(self,str_chrono):
        str_chrono = cleanup(str_chrono)
        try:
            dt = datetime.strptime(str_chrono,"%Hh%M'%S''")
        except ValueError:
            try:
                dt = datetime.strptime('00h' + str_chrono,"%Hh%M'%S''")
            except ValueError:
                dt = datetime.strptime('00h' + str_chrono,"%Hh%M:%S''")
        self.chrono = timedelta(hours=dt.hour,minutes=dt.minute,seconds=dt.second)

    def __str__(self):
            s=self.chrono.total_seconds()
            if int(s//3600) == 0:
                return "{}'{}''".format(int(s % 3600 // 60),int(s % 60))
            else:
                return "{:02}h{}'{}''".format(int(s//3600),int(s % 3600 //60),int(s % 60))

class Runner:
    """Runner"""
    def __init__(self,runner_ID='',name="unknown",club="unknown",category="XX",gender="X"):
        self.runner_ID=runner_ID
        self.bilans=[]
        self.name = name
        self.club = club
        self.category = category
        self.gender = gender

    def __str__(self):
        return 'ID: '+self.runner_ID+' name: '+self.name+' club: '+self.club+' category: '+self.category+' gender: '+self.gender

    def fetch_bilans(self,race_type=10):
        url_runner="http://bases.athle.com/asp.net/athletes.aspx?base=bilans&seq=" + str(strtohex(self.runner_ID))
        soup=extract_soup(url_runner)

        race_type_dict = {'10':"10 Km Route",'15':"15 Km Route",'21':"1/2 Marathon",'42':"Marathon"}
        race_type_str = race_type_dict[str(race_type)] # penser a faire un dictionnaire pour chaque type
        #de course

        for a in soup.find_all('tr'):
            if a.td.get_attribute_list('class')[0] == 'innerDatas':
                if a.td.next_sibling.next_sibling.string == race_type_str:
                    record = {}
                    for sib in a.previous_siblings:
                        try:
                           if sib.td.get_attribute_list('class')[0] == 'innersubLabels':
                                record['annee']=sib.td.string
                                break
                        except:
                            pass
                    record['temps']=Chrono(a.td.next_sibling.next_sibling.next_sibling.next_sibling.string)
                    self.bilans.append(record)

class Race:
    """Race"""
    def __init__(self,url):
        self.urlFFA = url
        self.results = []
        self.race_ID,self.epreuve=self.parse_url(self.urlFFA)
        self.errors = []

    def append_runner(self,runner,chrono):
        self.results.append({'temps':chrono,'runner':runner})

    def parse_url(self,urlFFA):
        race_ID=urlFFA.split("frmcompetition=")[1].split("&")[0]
        epreuve=urlFFA.split("frmepreuve=")[1]
        return race_ID,epreuve

    def subrace_bilans(self,rankinf,ranksup,years_list,race_type):
        # revoir plutot en fonction des coureurs dans la bdd
        results_=[]
        results_runner = []

        for i,r in enumerate(self.results[rankinf-1:ranksup]):
            print(r['runner'].name)
            if r['runner'].runner_ID:
                chrono = r['temps']
                runner = r['runner']
                runner.fetch_bilans(race_type)
                results_runner = []
                l_bil=runner.bilans[:]
                _=[l_bil.append({'temps':'-','annee':b}) for b in list(set(years_list)-set([b['annee'] for b in l_bil]))]
                results_runner=[b['temps'] for b in sorted([b for b in l_bil if b['annee'] in
                                       years_list],key=lambda
                                                     k:k['annee'],reverse=True)]
                results_runner.insert(0,runner.name)
                results_runner.insert(0,chrono)
                results_runner.insert(0,str(rankinf+i))
                results_.append(results_runner)
        return results_

    def fill_runner(self,line_runner): #line_runner is a <td> line corresponding to a runner
        runner = Runner()
        if line_runner[0][0].string == '-' or line_runner[2][0].string.split('(')[0].strip()=='Participant Invalide':
            runner.name = 'nom inconnu'
            runner.category = 'XX'
            runner.gender = 'X'
            runner.club='club inconnu'
            runner.runner_ID=''
            cr = self.results[-1]['temps'] #le chrono du
            self.errors.append('ligne ' + str(len(self.results)) + ': coureur invalide et remplacé par le coureur inconnu (sacré coureur inconnu!)')
        else:
            try:
                runner.runner_ID=str(line_runner[2]).split(",")[1].strip()
            except IndexError:
                runner.runner_ID=''

            runner.name=line_runner[2][0].string.split('(')[0].strip()
            runner.category=line_runner[6][0].string[:2] # runner category
            runner.gender=line_runner[6][0].string[2:] # runner category
            cr = Chrono(line_runner[1][0].string)
            if line_runner[3][0].string is None:
                runner.club=''
            else:
                runner.club=line_runner[3][0].string # runner club

        if runner.runner_ID: #insert runner with ID into the bdd
            bd.insert_runner(runner) # inject runner in table

        return runner, cr

    def extract_runners(self):
        # detect if race is already stored in database and extract only if
        # necessary
        if bd.check_race_new(self):
            print('Race already in database, will retrieve existing datas...')
            bd.fetch_race_results(self)
        else:
            print('Race not in database, need to download from FFA site...')
            bd.insert_race(self) #injects race in table
            soup=extract_soup(self.urlFFA)
            total_page_number=soup.find_all('select')[0].contents[0].string.split('/')[1].split('<')[0].strip()

            # retrieve maximum pas number if any

            # because when page number is equal to 1, no html tag with no total
            # page number
            try:
                total_page_number = int(total_page_number)
            except ValueError:
                total_page_number = 1

            for page_number in range(total_page_number): # check first value in
                url_page = self.urlFFA + "&frmposition=" + str(page_number)
                soup=extract_soup(url_page)

                for a in soup.find_all('tr'): #loop over all tr tags
                    if a.td.get_attribute_list('class')[0] in ('datas0','datas1'): 
                        runner_tmp=[]
                            # detect all tr wherein td has a td with datas0 or 1 class
                        for b in a.find_all('td'):
                            if b.get_attribute_list('class')[0] in ('datas0','datas1'):
                                # loop within a runner row
                                runner_tmp.append(b.contents)
                        runner,cr = self.fill_runner(runner_tmp)
                        self.append_runner(runner, cr)
                        bd.insert_race_results(runner,self)

    def populate(self):
        pass

    def write2csv(self,path_output,filename):
        with open(path_output + filename + '.csv', 'w',encoding='utf8') as f:
            f.write("class;temps;nom;cat;sexe;club\n")
            for i,rank in enumerate(self.results):
                f.write(str(i+1) + ";" + str(rank['temps']) + ";" +
                        rank['runner'].name + ";" + rank['runner'].category +
                        ";" + rank['runner'].gender + ";" + rank['runner'].club + ";\n")
            f.close()

def convert(url_base,path_output):
    if check_url(url_base):

        race=Race(url_base)
        race.extract_runners()

        race_ID_tmp=random.randint(1,100000)

        race.write2csv(path_output,'race_' + str(race_ID_tmp))
        return ('race_' + str(race_ID_tmp) + '.csv',race.errors)
    else:
        return (False,False)

def analyse(url_base,rankinf,ranksup,race_type=10,
            years_list=['2018','2017','2016','2015']):
    if check_url(url_base):
        if check_ranks(rankinf,ranksup)[0]:
            rankinf=check_ranks(rankinf,ranksup)[1]
            ranksup=check_ranks(rankinf,ranksup)[2]
            race=Race(url_base)
            race.extract_runners()
            bilans_=race.subrace_bilans(rankinf,ranksup,years_list,race_type)
            print(bilans_)
            return (True,bilans_)
        else:
            return (False,"Vérifiez les rangs")
    else:
        return (False,"l\'url du lien ne convient pas")

if __name__ == "__main__":
    """pour execution si demarrage en stand alone"""
    analyse('http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=184050&frmepreuve=30+Km',1,111,10)
