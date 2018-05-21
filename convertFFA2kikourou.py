from bs4 import BeautifulSoup
import re
import urllib
import random

def check_url(url):
    valid=re.compile(r"^(http://bases.athle.com/asp.net/liste.aspx\?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=[0-9]*&frmepreuve=)")
    return bool(valid.match(url))

def format_runner(runner):
    runner_=[]
    runner_.append(runner[0][0].string.encode('latin-1')) # runner rank
    runner_.append(runner[1][0].string.encode('latin-1')) # runner time
    runner_.append(runner[2][0].string.split('(')[0].strip().encode('latin-1')) # runner identity
    runner_.append(runner[6][0].string.encode('latin-1')) # runner category
    # because sometimes, club is defined by a space caracter instead of empty
    # string
    try:
        if runner[3][0].string.encode('latin-1') == '\xa0':
            runner_.append('')
        else:
            runner_.append(runner[3][0].string.encode('latin-1')) # runner club
    except AttributeError:
        runner_.append('')

    return runner_

def ffa2kikourou(url_base,path_output):
    if check_url(url_base):
        results=[] # initialize result list

        url = urllib.urlopen(url_base) # retrieve remote html page
        soup = BeautifulSoup(url,"lxml") # parse html page with lxml and bs
        total_page_number=soup.find_all('select')[0].contents[0].string.split('/')[1].split('<')[0].strip()
        # retrieve maximum pas number if any

        # because when page number is equal to 1, no html tag with no total
        # page number
        try:
            total_page_number = int(total_page_number)
        except ValueError:
            total_page_number = 1

        for page_number in range(total_page_number): # check first value in
        # html  page
            url_page = url_base + "&frmposition=" + str(page_number)

            url = urllib.urlopen(url_page)
            soup = BeautifulSoup(url,"lxml")

            for a in soup.find_all('tr'): #loop over all tr tags
                if a.td.get_attribute_list('class')[0] in ('datas0','datas1'): 
                        # detect all tr wherein td has a td with datas0 or 1 class
                    runner=[]
                    for b in a.find_all('td'):
                        if b.get_attribute_list('class')[0] in ('datas0','datas1'):
                            runner.append(b.contents)
                    results.append([i for i in format_runner(runner)])

        race_ID_tmp=random.randint(1,100000)
        race_ID=url_base.split('frmcompetition=')[1].split('&')[0]
        with open(path_output + 'race_' + str(race_ID_tmp) + '.csv', 'w') as f:
            print "class;temps;nom;cat;sexe;club"
            f.write("class;temps;nom;cat;sexe;club\n")
            for runner in results:
                print runner[0] + ";" + runner[1] + ";" + runner[2] + ";" + runner[3][:2] + ";" + runner[3][2:] + ";" + runner[4] + ";"
                f.write(runner[0] + ";" + runner[1] + ";" + runner[2] + ";" + runner[3][:2] + ";" + runner[3][2:] + ";" + runner[4] + ";\n")
        f.closed
        return (True,'race_' + str(race_ID_tmp) + '.csv')
    else:
        return (False,'')
