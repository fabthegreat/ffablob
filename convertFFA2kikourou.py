from bs4 import BeautifulSoup

import urllib
#url = urllib.urlopen("http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=205707&frmepreuve=1%2f2+Marathon+TC")
url = urllib.urlopen("/home/ftg/Documents/Programmation/python/ffablob/CompetitionsResults.html")


soup = BeautifulSoup(url,"lxml")

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

# loop over each page of results
#

results=[]
for a in soup.find_all('tr'): #loop over all tr tags
    if a.td.get_attribute_list('class')[0] in ('datas0','datas1'): # detect all tr wherein td has a td with datas0 or 1 class
        runner=[]
        for b in a.find_all('td'):
            if b.get_attribute_list('class')[0] in ('datas0','datas1'):
                runner.append(b.contents)
#        print runner
        results.append([i for i in format_runner(runner)])
#        results.append(runner)

for runner in results:
#    print("\n")
#    print("###################")
#    print("Runner " + str(runner[0]))
#    print("###################")
    print runner




