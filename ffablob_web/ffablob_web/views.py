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
    # check GET datas
    # retrieve URL
    if request.method == 'GET' and 'urlFFA' in request.GET and \
    request.GET['urlFFA']:
        # check URL
        urlFFA = request.GET['urlFFA']
        if utils.check_urlFFA(urlFFA):
            race_ID,racetype = utils.extract_race_from_url(urlFFA)
            race = design.Race(race_ID,racetype)
            if request.session.get('races'):
                request.session['races'].append([race.ID,race.racetype])
                request.session.modified = True
            else:
                request.session['races']=[[race.ID,race.racetype]]
            error_msg_url = 'Course chargée dans votre liste!'

            #error_msg_url = ';'.join([race_id[0] for race_id in request.session['races']])
            #race.extract_runners_from_race()
            # create a race from provided URL
            # process race
            # store race ID/racetype in a session
            # print race information with toggle (+remove button)
            return render(request,'statistics.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races'),'results':race.results})
        else:
            error_msg_url = 'Veuillez renseigner une URL valide'
            return render(request,'statistics.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

    error_msg_url = 'Veuillez renseigner une URL dans la boîte de dialogue'
    return render(request,'statistics.html',{'error_msg_url':error_msg_url,'racelist':request.session.get('races')})

def flush_cart(request):
    request.session.clear()
    request.session.modified = True
    return redirect('/')
