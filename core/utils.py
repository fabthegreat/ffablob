from bs4 import BeautifulSoup
import re
import urllib.request
import random
from datetime import datetime,timedelta
import sys

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
                    i = list(map(lambda x:str(x),result_line_flat))

        return result_lines

def correct_resultlines(result_lines):
        # all corrections operations on lines are made here
        rls=[]
        for result_line in result_lines:
            if result_line[0] == '-':
                # replace some values with arbitrary ones
                result_line = ['-'] * 9
            else:
                # extract runner ID before other filter operations
                try:
                    ID=str(result_line[2]).split(",")[1].strip()
                except IndexError:
                    ID=''

                result_line = list(map(lambda x: x.string,result_line))
            result_line.insert(3,ID)
            rls.append(result_line)
            print(result_line)
        return rls

