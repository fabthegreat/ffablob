import re
import os.path
from subprocess import Popen, PIPE
import shutil
import tempfile
import urllib.request
import utils
import sys

def check_file(path, file_name, file_type = 'PDF'):
    with Popen(['/usr/bin/file','-b',path + '/' + file_name], stdout=PIPE) as p:
        output = [o for o in p.stdout]
        if file_type == 'PDF' and output[0].decode('utf8').rstrip()[:3] == file_type:
            return True
        elif file_type == 'text' and output[0].decode('utf8').split(' ')[1].rstrip() == file_type:
            return True
        else:
            Popen(['/bin/rm',path + '/' + file_name], stdout=PIPE)
            return False

def handle_uploaded_file(path,file, file_type = 'PDF'):
    destination = open(path + '/' + file.name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    return check_file(path,file.name, file_type)

def handle_remote_file(url,path,file_name='', file_type = 'PDF'):
    if not file_name:
        file_name = url.split('/')[-1]

    with urllib.request.urlopen(url) as response:
        with open(path + '/' + file_name, 'wb+') as out_file:
            shutil.copyfileobj(response, out_file)
    return check_file(path,file_name, file_type)

def lines_from_pdf(path,file_name):
    with Popen(['pdftotext','-layout',path + '/' + file_name,'-'], stdout=PIPE, bufsize=1) as p:
            for line in p.stdout:
                yield line.decode('utf-8')
                #yield line.decode('ISO_8859-1')

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
    if organization in ('l-chrono','protiming','sportips','fichier générique','e-run63'):
            print("ligne à traiter: " + line)
            time, time_error = fetch_catch_column_errors(r'\b\d{2}:\d{2}:\d{2}\b',line,0)
            rank, rank_error = fetch_catch_column_errors(r'\d+',line,0)
            name, name_error = fetch_catch_column_errors(r'\b((?:[a-zA-ZÄÉÊÈËÎÏÔÖÛÜäéêèëîïôöûüç\'\-]+\s?)+)\b',line,0)
            club, club_error = fetch_catch_column_errors(r'(\b(?:[a-zA-ZÄÉÊÈËÎÏÔÖÛÜäéêèëîïôöûüç\'\-]+\s?)+\b|/)',line,-1)
            #TODO :check in a more elegant manner when only 1 long word sequence has been found (and then name == club)
            #TODO : check when digits are in the club name
            if club == name:
                club = ''
                club_error = True

            catg,catg_error = fetch_catch_column_errors(r'\b[JBCVEMS][A-Z1-4][HMF]\b',line,0)
#            print(catg)
            if catg:
                cat = catg[:2]
                gender = catg[-1]
            else:
                cat = ''
                gender = ''

    elif organization in ('yaka-events'):
            print("ligne à traiter: " + line)
            time, time_error = fetch_catch_column_errors(r'\b\d{2}:\d{2}:\d{2}\b',line,0)
            rank, rank_error = fetch_catch_column_errors(r'\d+',line,0)
            name, name_error = fetch_catch_column_errors(r'\b((?:[a-zA-ZÄÉÊÈËÎÏÔÖÛÜäéêèëîïôöûüç\'\-]+\s?)+)\b',line,0)
            club, club_error = fetch_catch_column_errors(r'(?:[a-zA-ZÄÉÊÈËÎÏÔÖÛÜäéêèëîïôöûüç\'\-]+\s?)+(?=\s+\d{2}:\d{2}:\d{2})\b',line,0)
            #TODO : check when digits are in the club name
            if club == name:
                club = ''

            catg,catg_error = fetch_catch_column_errors(r'\b[JBCVEMS][A-Z1-4][MF](?=\()',line,0)
            if catg:
                cat = catg[:2]
                gender = catg[-1]
            else:
                cat = ''
                gender = ''

    elif organization in ('jmg-chrono'):
            print("ligne à traiter: " + line)
            time, time_error = fetch_catch_column_errors(r'\b\d{0,2}:{0,1}\d{2}:\d{2}\b',line,0)
            rank, rank_error = fetch_catch_column_errors(r'\d+',line,0)
            name_1, name_error = fetch_catch_column_errors(r'\b((?:[a-zA-ZÄÉÊÈËÎÏÔÖÛÜäéêèëîïôöûüç\'\-]+)+)\b',line,2)
            name_2, name_error = fetch_catch_column_errors(r'\b((?:[a-zA-ZÄÉÊÈËÎÏÔÖÛÜäéêèëîïôöûüç\'\-]+)+)\b',line,3)
            name = name_1 + ' ' + name_2.title()
            club, club_error = fetch_catch_column_errors(r'\b((?:[a-zA-ZÄÉÊÈËÎÏÔÖÛÜäéêèëîïôöûüç\'\-]+\s?)+)\b',line,4)
            #TODO : check when digits are in the club name
            if club == name:
                club = ''

            catg,catg_error = fetch_catch_column_errors(r'\b[JBCVEMS][A-Z1-4][MF]\b',line,0)
            if catg:
                cat = catg[:2]
                gender = catg[-1]
            else:
                cat = ''
                gender = ''
            if club == gender:
                club = ''

    line = [rank,time,name,cat,gender,club]
    errors = [rank,{'time_error':time_error,'rank_error':rank_error,'name_error':name_error,'club_error':club_error,'catg_error':catg_error}]
    print(line)
    #print(errors)
    return line,errors

def write_to_csv(result_tab,path,filename):
    with open(path + '/' + filename + '.csv', 'w',encoding='ISO_8859-1') as f:
        f.write("class;temps;nom;cat;sexe;club\n")
        for r in result_tab:
            rw=r[:] #shallow copy to preserve results
            f.write(';'.join(map(lambda x: str(x),rw))+'\n')
    f.close()
    return 'pdf_files/' + filename + '.csv'

def check_csv_kikourou(path,file_name):
    """ Check if a csv file is ok to be sent on Kikourou """

    # retrieve datas from file
    with open(path + '/' + file_name, 'r',encoding ='ISO_8859-1') as f:
        file_header = f.readline().rstrip()
        file_data = f.readlines()

    results = []
    errors = []
    for fd in file_data:
        results.append({'rank':fd.split(';')[0],'time':fd.split(';')[1],'runner_name':fd.split(';')[2],'cat':fd.split(';')[3],'gender':fd.split(';')[4]})
        errors.append({})


    def encoding_check(path = path, file_name = file_name):
        with Popen(['/usr/bin/file','-b',path + '/' + file_name], stdout=PIPE) as p:
            output = [o for o in p.stdout]
            file_infos = [o.decode('utf8').rstrip() for o in output][0]
            #TODO: try...except
            file_infos = [file_infos.split(' ')[0],file_infos.split(' ')[1]]
            if (file_infos[0],file_infos[1]) == ('ISO-8859','text'):
               return True, "Encodage du fichier correct"
            else:
               return False,"Encodage du fichier NOK (devrait être ISO-8859)"

    def header_check():
        if file_header == 'class;temps;nom;cat;sexe;club':
            return True, "En-tête du fichier OK"
        else:
            return False, "En-tête du fichier NOK (devrait être 'class;temps;nom;cat;sexe;club')"

    def rank_check():
        for i,r in enumerate(results):
            if i+1 != int(r['rank']):
                errors[i]['rank']= False
            else:
                errors[i]['rank']= True

    def time_check():
        time_patterns = [r'\b\d{1,3}:\d{1,3}:\d{1,3}\b', r'\b\d{1,3}:\d{1,3}\b',
                   r'\b\d{1,3}h\d{1,3}\'\d{1,3}\"']
        # check why which a trailing \b pattern doesn't work for second pattern
        for i,r in enumerate(results):
            if not utils.check_pattern(time_patterns,r['time']):
                errors[i]['time']= False
            else:
                errors[i]['time']= True

    def cat_check():
        cat_patterns = [r'\b[SCVJE][ESUA12345]\b']
        for i,r in enumerate(results):
            if not utils.check_pattern(cat_patterns,r['cat']):
                errors[i]['cat']= False
            else:
                errors[i]['cat']= True

    def gender_check():
        gender_patterns = [r'\b[FM]\b']
        for i,r in enumerate(results):
            if not utils.check_pattern(gender_patterns,r['gender']):
                errors[i]['gender']= False
            else:
                errors[i]['gender']= True

    def allfields_check():
        # forbidden caracters check
        #if err_gender:
        all_fields = [ r.split(';') for r in file_data ]
        fields_patterns = [r'[.\\]']
        for i,line in enumerate(all_fields):
            for field in line:
                if utils.check_pattern(fields_patterns,field, True):
                    errors[i]['field']= False
                else:
                    errors[i]['field']= True

    check_list = [encoding_check, header_check, rank_check, time_check, cat_check, gender_check, allfields_check]

    def chain_check(check_list):
        for f in check_list:
            f()

    chain_check(check_list)

    return zip(results,errors)

if __name__ == '__main__':

    if sys.argv[1] == 'lookup':

        for l in lines_from_pdf('/home/ftg/python/ffablob/tests','test-chrono-start.pdf'):
            fl = filter_line(l)
            if fl:
                fl = organize_columns(fl,'l-chrono')

    else:
        pass
