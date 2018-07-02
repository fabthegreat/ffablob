import sys
import os
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

def main(request, results = None):
    return render(request,'index.html',{'racelist':request.session.get('races')})

def load_race(request):
    if request.method == 'GET' and 'urlFFA' in request.GET and \
    request.GET['urlFFA']:
        # check URL
        urlFFA = request.GET['urlFFA']
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
    # TODO: all
#    if request.method == 'GET' and 'urlFFA' in request.GET and \
    race = design.Race(race_ID,race_type)
    error_msg_url = 'Chargement de l\'analyse effectuée'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

def csv_export(request,race_ID,race_type):
    race = design.Race(race_ID,race_type)
    csvfile_link = race.write_to_csv(root_path + project_path + static_path + '/race_files',race_ID + '_' + race_type)
    error_msg_url = 'Fichier csv généré'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'csvfile':csvfile_link})
