from bs4 import BeautifulSoup
import re
import urllib.request
import random
from datetime import datetime,timedelta
import sys

import design

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

def extract_resultlines(urlFFA):
        soup = extract_soup(urlFFA)
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
                            # loop within a runner row
                            result_line.append(b.contents)
                    # Transform each result line in a runner
                    result_line_flat=[i[0] for i in result_line]
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
            result_line[1]=design.Time(result_line[1]) # transform string
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
                        record['time']=design.Time(a.td.next_sibling.next_sibling.next_sibling.next_sibling.string)
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

if __name__ == "__main__":
        runner=design.Runner('528136','unknown','XX','X','DDDD')
        correct_records(extract_records(runner))

        print(DBcolumn_to_dateracetype('record_10k_2015'))
        print(dateracetype_to_DBcolumn('2015','2015'))
