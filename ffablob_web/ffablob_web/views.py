import sys
import os
import copy
from django.http import HttpResponse
from django.shortcuts import render,redirect


root_path="/var/www"
project_path = "/ffablob"
core_module_path = "/core"
static_path  = "/ffablob_web/static"
sys.path.insert(0,root_path + project_path)
sys.path.insert(0,root_path + project_path + core_module_path)

import design
import utils
import orgapdf
import statraces

def main(request):
    return render(request,'index.html',{'racelist':request.session.get('races')})

def compare(request):
    tab_comparison = []
    races = []
    error_msg_url=''
    if request.method == 'POST':
        for i,v in request.POST.items():
            if 'option_' in i:
                races.append(design.Race(v.split('/')[0],v.split('/')[1]))
                error_msg_url += races[-1].ID + ' ' + races[-1].racetype


    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'selected_races':races})


def convert(request):
    file_link = ''
    file_name = ''
    error_log = []
    tabfl = []

    if request.method == 'POST' and 'file' in request.FILES:
            file = request.FILES['file']
            orga = request.POST['timecompany']
            error_log = ['Le fichier de {} a été correctement converti.'.format(orga)]
            file_fullpath = root_path + project_path + static_path + '/pdf_files'
            #TODO: handle files that are not pdf: remove them from harddisk
            if orgapdf.handle_uploaded_file(file_fullpath,file):
                for l in orgapdf.lines_from_pdf(file_fullpath,file.name):
                    fl = orgapdf.filter_line(l)
                    if fl:
                        #TODO: add protiming orga with dict
                        try:
                            fl,errors = orgapdf.organize_columns(fl,orga.lower())
                        except:
                            error_log = ['Les colonnes du fichiers ne correspondent pas à l\'organisation spécifiée']
                            return render(request,'convert.html',{'convert':True,'error_log':error_log,'file':file_link,'test_chunks':file_name})

                        if [key for key in errors[1].keys() if errors[1][key]]:
                            error_log.append('ATTENTION: vérifiez la ligne {} du fichier.'.format(errors[0]))

                        tabfl.append(fl)
                        file_name = file.name[:-4]
                        file_link = orgapdf.write_to_csv(tabfl,file_fullpath,file.name[:-4])
            else:
                error_log = ['Le fichier envoyé n\'est pas un pdf valide.']

    return render(request,'convert.html',{'convert':True,'error_log':error_log,'file':file_link,'test_chunks':file_name})

def load_race(request):
    if request.method == 'POST' and 'urlFFA' in request.POST and \
    request.POST['urlFFA']:
        # check URL
        urlFFA = request.POST['urlFFA']
        if utils.check_urlFFA(urlFFA):
            race_ID,racetype = utils.extract_race_from_url(urlFFA)
            race = design.Race(race_ID,racetype)
            error_msg_url=append_race_to_list(request,race)
            return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results})
        else:
            error_msg_url = 'Veuillez renseigner une URL valide'
            return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

    error_msg_url = 'Veuillez renseigner une URL dans la boîte de dialogue'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

def flush_cart(request):
    request.session.clear()
    request.session.modified = True
    error_msg_url = "Liste de course supprimée!"
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

def remove_race(request,race_ID,race_type):
    if request.session.get('races') and utils.index_shortlist_in_list([race_ID,race_type],request.session['races']) is not None:
        request.session['races'].pop(utils.index_shortlist_in_list([race_ID,race_type],request.session['races']))
        request.session.modified = True
        error_msg_url = 'Course supprimée avec succès!'
    else:
        error_msg_url = "La course n'appartient pas à votre liste!"
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

def append_race_to_list(request,race):
    if request.session.get('races'):
        if [race.ID,race.racetype,race.name] not in request.session['races']:
            request.session['races'].append([race.ID,race.racetype,race.name])
            request.session.modified = True
            error_msg_url = 'Course chargée dans votre liste!'
        else:
            error_msg_url = 'Course déjà dans votre liste!'
    else:
        request.session['races']=[[race.ID,race.racetype,race.name]]
        error_msg_url = 'Course chargée dans votre liste!'
    return error_msg_url

def show_race(request,race_ID,race_type):
    # TODO: check Race_ID & racetype are in DB
    race = design.Race(race_ID,race_type)
    error_msg_url = 'Course affichée'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results})

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
