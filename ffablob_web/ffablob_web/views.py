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

            #error_msg_url = ';'.join([race_id[0] for race_id in request.session['races']])
            #race.extract_runners_from_race()
            # create a race from provided URL
            # process race
            # store race ID/racetype in a session
            # print race information with toggle (+remove button)
            return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results})
        else:
            error_msg_url = 'Veuillez renseigner une URL valide'
            return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

    error_msg_url = 'Veuillez renseigner une URL dans la boîte de dialogue'
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})


def flush_cart(request):
    request.session.clear()
    request.session.modified = True
    return redirect('/')

def remove_race(request,race_ID,race_type):
    if request.session.get('races') and [race_ID,race_type] in request.session['races']:
        request.session['races'].remove([race_ID,race_type])
        request.session.modified = True
        error_msg_url = 'Course supprimée avec succès!'
    else:
        error_msg_url = "La course n'appartient pas à votre liste!"
    return render(request,'index.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})


def append_race_to_list(request,race):
    if request.session.get('races'):
        if [race.ID,race.racetype] not in request.session['races']:
            request.session['races'].append([race.ID,race.racetype])
            request.session.modified = True
            error_msg_url = 'Course chargée dans votre liste!'
        else:
            error_msg_url = 'Course déjà dans votre liste!'
    else:
        request.session['races']=[[race.ID,race.racetype]]
        error_msg_url = 'Course chargée dans votre liste!'
    return error_msg_url
