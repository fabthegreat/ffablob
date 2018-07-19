import re
from subprocess import Popen, PIPE

def check_file(path,file_name):
    with Popen(['/usr/bin/file','-b',path + '/' + file_name], stdout=PIPE) as p:
        output = [o for o in p.stdout]
        if output[0].decode('utf8').rstrip()[:3] == 'PDF':
            return True
        else:
            Popen(['/bin/rm',path + '/' + file_name], stdout=PIPE)
            return False

def handle_uploaded_file(path,file):
    destination = open(path + '/' + file.name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    if check_file(path,file.name):
        return True
    else:
        return False


def lines_from_pdf(path,file_name):
    with Popen(['pdftotext','-layout',path + '/' + file_name,'-'], stdout=PIPE, bufsize=1) as p:
            for line in p.stdout:
                yield line.decode('utf-8')

def filter_line(line):
    l=line[:]
    tabl=[line[0:4].strip()]
    try:
        int(tabl[0])
    except:
        return None
    return l

def parse_columns(line,columns_size):
    string_tab=[]
    start=0
    for c in columns_size:
        string_tab.append(line[start:start+c])
        start = start + c
    return string_tab

def fetch_catch_column_errors(regex,line,index):
    error = False
    try:
        found = re.findall(regex,line)[index]
    except:
        error = True
        return '', error
    return found,error

def organize_columns(line,organization):
    """ Will output values to construct csv files depending on pattern of
    organization file 
    """
    #TODO: handle errors for each regex
    if organization in ('l-chrono','protiming','sportips','fichier générique'):
            print(line)
            time, time_error = fetch_catch_column_errors(r'\b\d{2}:\d{2}:\d{2}\b',line,0)
            rank, rank_error = fetch_catch_column_errors(r'\d+',line,0)
            name, name_error = fetch_catch_column_errors(r'\b((?:[a-zA-ZÎÏÔÛÜÉÈéèîëï\']+\s?)+)\b',line,0)

            club, club_error = fetch_catch_column_errors(r'(\b(?:[a-zA-Zéè]+\s?)+\b|/)',line,-1)
            #TODO :check in a more elegant manner when only 1 long word sequence has been found (and then name == club)
            #TODO : check when digits are in the club name
            if club == name:
                club = ''
                club_error = True

            catg,catg_error =fetch_catch_column_errors(r'\b[JBCVEMS][A-Z1-4][MF]\b',line,0)
            print(catg)
            if catg:
                cat = catg[:2]
                gender = catg[-1]
            else:
                cat = ''
                gender = ''

    if organization in ('yaka-events'):
            print(line)
            time, time_error = fetch_catch_column_errors(r'\b\d{2}:\d{2}:\d{2}\b',line,0)
            rank, rank_error = fetch_catch_column_errors(r'\d+',line,0)
            name, name_error = fetch_catch_column_errors(r'\b((?:[a-zA-Z\-ÎÏÔÛÜÉÈéèîëï\']+\s?)+)\b',line,0)
            club, club_error = fetch_catch_column_errors(r'(?:[a-zA-Zéè\-\']+\s?)+(?=\s+\d{2}:\d{2}:\d{2})\b',line,0)
            #TODO : check when digits are in the club name
            if club == name:
                club = ''

            catg,catg_error =fetch_catch_column_errors(r'\b[JBCVEMS][A-Z1-4][MF](?=\()',line,0)
            if catg:
                cat = catg[:2]
                gender = catg[-1]
            else:
                cat = ''
                gender = ''


    line = [rank,time,name,cat,gender,club]
    errors = [rank,{'time_error':time_error,'rank_error':rank_error,'name_error':name_error,'club_error':club_error,'catg_error':catg_error}]
    print(line)
    print(errors)
    return line,errors

def write_to_csv(result_tab,path,filename):
    with open(path + '/' + filename + '.csv', 'w',encoding='utf8') as f:
        f.write("class;temps;nom;cat;sexe;club\n")
        for r in result_tab:
            rw=r[:] #shallow copy to preserve results
            f.write(';'.join(map(lambda x: str(x),rw))+'\n')
    f.close()
    return 'pdf_files/' + filename + '.csv'


if __name__ == '__main__':
    tabfl = []
#    print(check_file('/home/ftg/python/ffablob/tests','emt_run_5.pdf'))

    for l in lines_from_pdf('/home/ftg/python/ffablob/tests','test_yaka.pdf'):
#        print(l)
        fl = filter_line(l)
        if fl:
            fl = organize_columns(fl,'yaka-events')
            tabfl.append(fl)

    #print(tabfl)
