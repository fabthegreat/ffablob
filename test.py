from bs4 import BeautifulSoup

import urllib 
url = urllib.urlopen("http://bases.athle.com/asp.net/liste.aspx?frmpostback=true&frmbase=resultats&frmmode=1&frmespace=0&frmsaison=2018&frmclub=&frmnom=LUCE&frmprenom=Fabien&frmsexe=&frmlicence=&frmdepartement=&frmligue=&frmcomprch=")


soup = BeautifulSoup(url,"lxml")


for a in soup.find_all("td",class_="datas0"):
    print(a.strin)



