import sys
import os
import copy
from django.http import HttpResponse
from django.shortcuts import render,redirect
import urllib.request


root_path="/var/www"
project_path = "/ffablob"
core_module_path = "/core"
static_path  = "/ffablob_web/static"
sys.path.insert(0,root_path + project_path)
sys.path.insert(0,root_path + project_path + core_module_path)

import design
import utils
import orgapdf
import statraces as strc
import db

def main(request):
    return render(request,'index.html',{'racelist':request.session.get('races')})

def search(request,sort_key='race_name'):
    searchresults=[]
    keys = {'date':3, 'ID':0, 'race_name':2, 'format': 4}
    if request.method == 'POST':
        searchresults = utils.prettify_search(db.search_DB(request.POST['searchphrase']))
        request.session['searchresults'] = sorted([list(sr) for sr in searchresults],key =lambda x:x[keys[sort_key]])
    else:
        request.session['searchresults'] = sorted(request.session['searchresults'],key =lambda x:x[keys[sort_key]])

    error_msg_url = 'Recherche affichée'

    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'searchresults':request.session['searchresults']})

def add_race(request,race_ID,race_type):
    # check if race_ID, racetype exist indeed in DB
    if 'searchresults' in request.session:
        searchresults = request.session['searchresults']
    else:
        searchresults = []
    race = design.Race(race_ID,race_type)
    error_msg_url=append_race_to_list(request,race)
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results,'searchresults':searchresults})

def reload_race(request,race_ID,race_type):
    # check if race_ID, racetype exist indeed in DB
    if 'searchresults' in request.session:
        searchresults = request.session['searchresults']
    else:
        searchresults = []
    race = design.Race(race_ID,race_type)
    race.resetDB()
    #error_msg_url=append_race_to_list(request,race)
    error_msg_url="Course mise à jour dans la base de données!"
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results,'searchresults':searchresults})

def compare(request):
    if 'searchresults' in request.session:
        searchresults = request.session['searchresults']
    else:
        searchresults = []
    tab_comparison = []
    races = []
    error_msg_url=''
    if request.method == 'POST':
        for i,v in request.POST.items():
            if 'option_' in i:
                races.append(design.Race(v.split('/')[0],v.split('/')[1]))
                strc.std_stat_table(races)

    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'selected_races':races,'searchresults':searchresults})

def check(request):
    error_log = []
    file_link = ''
    file_name = ''

    if request.method == 'POST' and ('file' in request.FILES):
            file_fullpath = root_path + project_path + static_path + '/csv_files'

            if 'file' in request.FILES:
                file = request.FILES['file']
                test_file = orgapdf.handle_uploaded_file(file_fullpath,file,'text')
                file_name = file.name

            if test_file:
                error_log = orgapdf.check_csv_kikourou(file_fullpath,file_name)

    return render(request,'check.html',{'convert':True,'error_log':error_log,'file':file_link,'test_chunks':file_name})

def convert(request):
    file_link = ''
    file_name = ''
    error_log = []
    tabfl = []

    if request.method == 'POST' and ('file' in request.FILES or
                                     request.POST['PDFfile']):
            orga = request.POST['timecompany']

            file_fullpath = root_path + project_path + static_path + '/pdf_files'
            #TODO: handle files that are not pdf: remove them from harddisk

            error_log = ['Le fichier envoyé n\'est pas un pdf valide.']

            if 'file' in request.FILES:
                file = request.FILES['file']
                test_file = orgapdf.handle_uploaded_file(file_fullpath,file)
                file_name = file.name
            elif request.POST['PDFfile']:
                try:
                    test_file = orgapdf.handle_remote_file(request.POST['PDFfile'],file_fullpath)
                    file_name = request.POST['PDFfile'].split('/')[-1]
                except:
                    error_log = ['L\'URL n\'est pas utilisable.']
                    test_file = False

            if test_file:
                for l in orgapdf.lines_from_pdf(file_fullpath,file_name):
                    fl = orgapdf.filter_line(l)
                    if fl:
                        try:
                            fl,errors = orgapdf.organize_columns(fl,orga.lower())
                        except:
                            error_log = ['Les colonnes du fichiers ne correspondent pas à l\'organisation spécifiée']
                            return render(request,'convert.html',{'convert':True,'error_log':error_log,'file':file_link,'test_chunks':file_name})

                        if [key for key in errors[1].keys() if errors[1][key]]:
                            error_log.append('ATTENTION: vérifiez la ligne {} du fichier.'.format(errors[0]))

                        tabfl.append(fl)

                file_name = file_name[:-4]
                file_link = orgapdf.write_to_csv(tabfl,file_fullpath,file_name)
                error_log = ['La cible {} a été correctement convertie.'.format(file_name)]

    return render(request,'convert.html',{'convert':True,'error_log':error_log,'file':file_link,'test_chunks':file_name})

def load_race(request):
    if 'searchresults' in request.session:
        searchresults = request.session['searchresults']
    else:
        searchresults = []

    if request.method == 'POST' and 'urlFFA' in request.POST and \
    request.POST['urlFFA']:
        # check URL
        urlFFA = request.POST['urlFFA']
        if utils.check_urlFFA(urlFFA):
            race_ID,racetype = utils.extract_race_from_url(urlFFA)
            race = design.Race(race_ID,racetype)
            error_msg_url=append_race_to_list(request,race)
            return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results,'searchresults':searchresults})
        else:
            error_msg_url = 'Veuillez renseigner une URL valide'
            return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'searchresults':searchresults})

    error_msg_url = 'Veuillez renseigner une URL dans la boîte de dialogue'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'searchresults':searchresults})

def flush_cart(request):
    searchresults = request.session['searchresults']
    request.session['races'].clear()
    request.session.modified = True
    error_msg_url = "Liste de course supprimée!"
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'searchresults':searchresults})

def remove_race(request,race_ID,race_type):
    if request.session.get('races') and utils.index_shortlist_in_list([race_ID,race_type],request.session['races']) is not None:
        request.session['races'].pop(utils.index_shortlist_in_list([race_ID,race_type],request.session['races']))
        request.session.modified = True
        error_msg_url = 'Course supprimée avec succès!'
    else:
        error_msg_url = "La course n'appartient pas à votre liste!"
    searchresults = request.session['searchresults']
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'searchresults':searchresults})

def append_race_to_list(request,race):
    if request.session.get('races'):
        if [race.ID,race.racetype,race.name,race.racetype_human] not in request.session['races']:
            request.session['races'].append([race.ID,race.racetype,race.name,race.racetype_human])
            request.session.modified = True
            error_msg_url = 'Course chargée dans votre liste!'
        else:
            error_msg_url = 'Course déjà dans votre liste!'
    else:
        request.session['races']=[[race.ID,race.racetype,race.name,race.racetype_human]]
        error_msg_url = 'Course chargée dans votre liste!'
    return error_msg_url

def show_race(request,race_ID,race_type):
    # TODO: check Race_ID & racetype are in DB
    if 'searchresults' in request.session:
        searchresults = request.session['searchresults']
    else:
        searchresults = []
    race = design.Race(race_ID,race_type)
    error_msg_url = 'Course affichée'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results,'searchresults':searchresults})

def load_analysis(request,race_ID,race_type):
    if request.method == 'POST' and 'RaceType' in request.POST and \
    request.POST['RaceType']:
        racetype_record = request.POST['RaceType']
        race = design.Race(race_ID,race_type)
        race.create_race_stats('meantime')
        race.create_race_stats('mediantime')
        race_recap={'name':race.name,'race_type':race.racetype,'id':race.ID,'runner_nb':len(race.results)}
        tab_records = []
        for i,r_ in enumerate(race.extract_runners_from_race()):
            timetabr = list(r_.list_records(racetype_record))
            tab_records.append((race.results[i]['rstl'][1],r_.name,timetabr))
        error_msg_url = 'Chargement de l\'analyse effectuée'
    else:
        error_msg_url = 'Il manque des informations de formulaire importantes!'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'race_recap':race_recap,'tab_records':tab_records,'race_stats':[race.race_stats['meantime'],race.race_stats['mediantime']]})

def csv_export(request,race_ID,race_type):
    race = design.Race(race_ID,race_type)
    csvfile_link = race.write_to_csv(root_path + project_path + static_path + '/race_files',race_ID + '_' + race_type)
    error_msg_url = 'Fichier csv généré'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'csvfile':csvfile_link})



