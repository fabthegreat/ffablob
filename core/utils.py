from bs4 import BeautifulSoup
import re
import urllib.request
import random
from datetime import datetime,timedelta
import sys

import design

def str_to_hms(str_time):
    str_time = cleanup(str_time)
    hms=re.findall('\d+',str_time)
    while len(hms)<3:
        hms.insert(0,'0')
    hms=list(map(lambda x: int(x),hms))
    return hms

def index_shortlist_in_list(slist,llist):
    if slist in list(map(lambda x:x[:len(slist)],llist)):
        return list(map(lambda x:x[:len(slist)],llist)).index(slist)

def check_urlFFA(url):
    valid=re.compile(r"^(http://bases.athle.com/asp.net/liste.aspx\?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=[0-9]*&frmepreuve=)")
    return bool(valid.match(url))

def extract_race_from_url(url):
        race_ID=url.split("frmcompetition=")[1].split("&")[0]
        racetype=url.split("frmepreuve=")[1]
        return (race_ID,racetype)

def cleanup(str_time):
        str_time = str_time.split(' ')[0].strip()
        return str_time

def strtohex(js_ID): # to retrieve runner_ID from javascript input
    hexreturn = ""
    for i in range(1,len(str(js_ID))+1):
        hexreturn += str(99 - ord(str(js_ID)[i - 1]))
        hexreturn += str(ord(str(js_ID)[i - 1]))
    return hexreturn

def DBcolumn_to_dateracetype(column_name):
    race_type=column_name.split('record_')[1].split('k')[0]
    date=column_name.split('record_')[1].split('k_')[1]
    return race_type,date

def dateracetype_to_DBcolumn(date,race_type):
    column_name='record_'+race_type+'k'+'_'+str(date)
    return column_name

def extract_soup(url):
        headers = { 'User-Agent' : 'Mozilla/5.0' }
        req = urllib.request.Request(url, None, headers)
        html = urllib.request.urlopen(req)
        soup = BeautifulSoup(html,"lxml") # parse html page with lxml and bs
        return soup

def extract_race(urlFFA):
    soup = extract_soup(urlFFA)
    race_name = extract_racename(soup)
    results = correct_resultlines(extract_resultlines(soup,urlFFA))
    return race_name,results

def extract_racename(soup):
    return soup.find(attrs={"class": "mainheaders"}).contents[0]

def extract_resultlines(soup,urlFFA):
        total_page_number = soup.find_all('select')[0].contents[0].string.split('/')[1].split('<')[0].strip()

        try:
            total_page_number = int(total_page_number)
        except ValueError:
            total_page_number = 1

        result_lines = []

        for page_number in range(total_page_number): # check first value in
            url = urlFFA + "&frmposition=" + str(page_number)
            soup=extract_soup(url)

            for a in soup.find_all('tr'): #loop over all tr tags
                if a.td.get_attribute_list('class')[0] in ('datas0','datas1'): 
                    result_line=[]
                    # detect all tr wherein td has a td with datas0 or 1 class
                    for b in a.find_all('td'):
                        if b.get_attribute_list('class')[0] in ('datas0','datas1'):
#                            print(b.contents)
                            # loop within a runner row
                            result_line.append(b.contents)
                    # Transform each result line in a runner
                    result_line_flat=[] #[i[0] for i in result_line]
                    for i,r in enumerate(result_line):
                        if i==1 and len(r)>1:
                            result_line_flat.append(r[1])
                        else:
                            result_line_flat.append(r[0])


                    result_lines.append(result_line_flat)

        return result_lines #list of flat lists of results

def correct_resultlines(result_lines):
        # all corrections operations on lines are made here
        rls=[]

        for i,result_line in enumerate(result_lines):
            error_code = 0 #default error code to 0
            if result_line[0] == '-' or result_line[2].string == 'Participant Invalide':
                error_code = 1
                # replace some values with arbitrary ones
                _rank = str(i+1)
                _time = result_lines[i-1][1].string
                _name = 'unknown'
                _club = ''
                _cat = ''
                result_line = [_rank,_time,_name,_club,'-','-',_cat,'-','-']

                ID = '' #to share same operation as for else section
            else:
                # extract runner ID before other filter operations
                try:
                    ID=str(result_line[2]).split(",")[1].strip()
                except IndexError:
                    ID=''

                # a few more corrections
                result_line = list(map(lambda x: x.string,result_line))
                for i,rl in enumerate(result_line):
                    if rl is None:
                        result_line[i] = ''
                result_line = list(map(lambda x: x.replace('\xa0',''),result_line))

            result_line.insert(3,ID) # insert ID saved earlier
            result_line.pop(5) # remove all the useless informations
            result_line.pop(5)
            result_line.pop(6)
            result_line.pop(6)
            result_line.insert(6,result_line[5][2:])
            result_line[5]=result_line[5][:2]
            result_line[1]=design.TimeNew.time_from_string(result_line[1].lstrip(' (').rstrip(')')) # transform string
#            print(result_line[1])
            #into Time object
            rls.append({'rstl':result_line,'errcode':error_code})
        return rls

def extract_records(runner):
        urlrunner="http://bases.athle.com/asp.net/athletes.aspx?base=bilans&seq="+ str(strtohex(runner.ID))
        soup = extract_soup(urlrunner)
        records = []

        race_type_dict = {'10':"10 Km Route",'15':"15 Km Route",'21':"1/2 Marathon",'42':"Marathon"}
        for u,v in race_type_dict.items():
            for a in soup.find_all('tr'):
                if a.td.get_attribute_list('class')[0] == 'innerDatas':
                    if a.td.next_sibling.next_sibling.string == v:
                        record = {}
                        for sib in a.previous_siblings:
                            try:
                               if sib.td.get_attribute_list('class')[0] == 'innersubLabels':
                                    record['year']=sib.td.string
                                    break
                            except:
                                pass
                        record['time']=design.TimeNew.time_from_string(a.td.next_sibling.next_sibling.next_sibling.next_sibling.string)
                        record['racetype']=u
                        records.append(record)
        return records

def correct_records(records):
        yearnow= datetime.now().year
        yearlist = [yearnow - i for i in range(4)]
        racetypes=['10','15','21','42']
        columnlist = {'record_'+rt+'k_'+str(y):None for rt in racetypes for y in
                      yearlist}

        for r in records:
            if r['year'] in str(yearlist) and r['racetype'] in racetypes:
                rcolumn=dateracetype_to_DBcolumn(r['year'],r['racetype'])
                columnlist[rcolumn]=r['time']

        return columnlist

def extract_race_list(league,department,year,month):
    #http://bases.athle.com/asp.net/liste.aspx?frmpostback=true&frmbase=calendrier&frmmode=1&frmespace=0&frmsaison=2018&frmtype1=Hors+Stade&frmtype2=&frmtype3=&frmtype4=&frmniveau=&frmniveaulab=&frmligue=ARA&frmdepartement=074&frmepreuve=&frmdate_j1=01&frmdate_m1=10&frmdate_a1=2018&frmdate_j2=01&frmdate_m2=11&frmdate_a2=2018
    #http://bases.athle.com/asp.net/liste.aspx?frmpostback=true&frmbase=calendrier&frmmode=1&frmespace=0&frmsaison=2018&frmtype1=Hors+Stade&frmtype2=&frmtype3=&frmtype4=&frmniveau=&frmniveaulab=&frmligue=ARA&frmdepartement=074&frmepreuve=&frmdate_j1=01&frmdate_m1=10&frmdate_a1=2018&frmdate_j2=01&frmdate_m2=11&frmdate_a2=2018

        url_core = 'http://bases.athle.com/asp.net/liste.aspx?frmpostback=true&frmbase=calendrier&frmmode=1&frmespace=0&frmsaison=' + year + '&frmtype1=Hors+Stade&frmtype2=&frmtype3=&frmtype4=&frmniveau=&frmniveaulab='
        url_main_param = '&frmligue=' + league + '&frmdepartement=' + department + '&frmepreuve='
        url_dates_param = '&frmdate_j1=01&frmdate_m1=' + month + '&frmdate_a1=' + year + '&frmdate_j2=01&frmdate_m2=' + str(int(month)+1) +'&frmdate_a2=' + year
        url = url_core + url_main_param + url_dates_param
        print(url)

        soup = extract_soup(url)
        list_ID = []
        for a in soup.find_all('td'):
            for b in a.get_attribute_list('class'):
                if b == 'listResCom':
                    list_ID.append(a.a['href'].split('frmcompetition=')[1])
        return list_ID

def extract_race_type(race_ID):
        soup = extract_soup('http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=' + race_ID)
        list_race_type = []
        for a in soup.find_all('select'):
            for b in a.find_all('option'):
#                print('select.option ---------\n' + str(a.option.contents[0]) + '\n ------------')
#                print('option ---------\n' + str(b) + '\n -----------')
                if a.option.contents[0] == 'Liste des Epreuves' and b['value']: #TODO: trouver pourquoi plusieurs chiffres sont detectés
                    list_race_type.append(b['value'])
        return list(set(list_race_type))

def prettify_search(search_rst):
    """ remove unnecessary elements in each tuple element and then create a set
    of results
    """
    rstl = []
    # add correct distance
    for srst in search_rst:
        # add pretty print of race format
        format_ted = urllib.parse.unquote(srst[1]).replace('+',' ')
        format_ted = format_ted.replace('TC','')
        #[ID,race_format,race name,date,race_format_human}
        race_name_pretty = srst[10].lower().title()
        rstl.append([srst[0],srst[1],race_name_pretty,srst[11],format_ted])

    return set([tuple(i) for i in rstl])

#TODO decorators? for all type of pattern?
def check_pattern(patterns, string, search = False):

    if not search:
        for p in patterns:
            if re.match(p,string):
                return True
        print(string,p) # prints false value (for debug)
        return False
    else:
        for p in patterns:
            if re.search(p,string):
                return True
                print(string,p) # prints true value (for debug)
        return False








if __name__ == "__main__":
    # import  importlib
    # importlib.reload(module)
    urlFFA='http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=205519&frmepreuve=1%2f2+Marathon+TC'
    soup=extract_soup(urlFFA)
    results=extract_resultlines(soup,urlFFA)
    print(results)

#        runner=design.Runner('528136','unknown','XX','X','DDDD')
#        correct_records(extract_records(runner))
#
#        print(DBcolumn_to_dateracetype('record_10k_2015'))
#        print(dateracetype_to_DBcolumn('2015','2015'))

#        yearnow = datetime.now().year
#        monthnow = datetime.now().month
#        monthnow = '09'
#        for race in extract_race_list('ARA','074',str(yearnow),str(monthnow)):
#            for race_type in extract_race_type(race):
#                print('race {}: format {}'.format(race,race_type))
#                race_temp = design.Race(race,race_type)
#            print(extract_race_type('212125'))
