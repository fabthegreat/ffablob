from bs4 import BeautifulSoup

import urllib
url_base="http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=205707&frmepreuve=1%2f2+Marathon+TC"
#url = urllib.urlopen("/home/ftg/Documents/Programmation/python/ffablob/CompetitionsResults.html")
url_base="http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=205572&frmepreuve=10+Km+Route+TC"

def format_runner(runner):
        runner_=[]
        runner_.append(runner[0][0].string.encode('latin-1'))
        runner_.append(runner[1][0].string.encode('latin-1'))
        runner_.append(runner[2][0].string.split('(')[0].strip().encode('latin-1'))
        runner_.append(runner[6][0].string.encode('latin-1'))
        try:
            if runner[3][0].string.encode('latin-1') == '\xa0':
                runner_.append('')
            else:
                runner_.append(runner[3][0].string.encode('latin-1'))
        except AttributeError:
            runner_.append('')

        return runner_

def ffa2kikourou(url_base,path_output):
        # loop over each page of results
    #
    results=[]

    url = urllib.urlopen(url_base)
    soup = BeautifulSoup(url,"lxml")
    total_page_number=soup.find_all('select')[0].contents[0].string.split('/')[1].split('<')[0].strip()

    print "Total page number: " + str(total_page_number)
    for page_number in range(int(total_page_number)):
        url_page = url_base + "&frmposition=" + str(page_number)
        print "Page number: " + str(page_number)

        url = urllib.urlopen(url_page)
        soup = BeautifulSoup(url,"lxml")

        for a in soup.find_all('tr'): #loop over all tr tags
            if a.td.get_attribute_list('class')[0] in ('datas0','datas1'): # detect all tr wherein td has a td with datas0 or 1 class
                runner=[]
                for b in a.find_all('td'):
                    if b.get_attribute_list('class')[0] in ('datas0','datas1'):
                        runner.append(b.contents)
        #        print runner
                results.append([i for i in format_runner(runner)])
        #        results.append(runner)

    with open(path_output + 'test.csv', 'w') as f:
        print "class;temps;nom;cat;sexe;club"
        f.write("class;temps;nom;cat;sexe;club\n")
        for runner in results:
        #    print("\n")
        #    print("###################")
        #    print("Runner " + str(runner[0]))
        #    print("###################")
            print runner[0] + ";" + runner[1] + ";" + runner[2] + ";" + runner[3][:2] + ";" + runner[3][2:] + ";" + runner[4] + ";"
            f.write(runner[0] + ";" + runner[1] + ";" + runner[2] + ";" + runner[3][:2] + ";" + runner[3][2:] + ";" + runner[4] + ";\n")
    f.closed

#ffa2kikourou(url_base)
