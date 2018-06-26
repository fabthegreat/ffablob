import sys
import os
from django.http import HttpResponse
from django.shortcuts import render


root_path="/var/www"
project_path = "/ffablob"
core_module_path = "/core"
static_path  = "/ffablob_web/static"
sys.path.insert(0,root_path + project_path)
sys.path.insert(0,root_path + project_path + core_module_path)

import design
import utils

def main(request):
    #   race_1 = design.Race('184050','30+Km')
    # check GET datas
    # retrieve URL
    error_msg_url = ''
    if request.method == 'GET' and 'urlFFA' in request.GET and \
    request.GET['urlFFA']:
        # check URL
        urlFFA = request.GET['urlFFA']
        if utils.check_urlFFA(urlFFA):
            race_ID,racetype = utils.extract_race_from_url(urlFFA)
            race = design.Race(race_ID,racetype)
            request.session['races'].append([race.ID,race.racetype])
            error_msg_url = 'Race ID: {}'.format(request.session['races'][0][0])
            #race.extract_runners_from_race()
            # create a race from provided URL
            # process race
            # store race ID/racetype in a session
            # print race information with toggle (+remove button)
            return render(request,'statistics.html',{'error_msg_url':error_msg_url,'results':race.results})
        else:
            error_msg_url = 'Veuillez renseigner une URL valide'
            #display error
    else:
        error_msg_url = 'Veuillez renseigner une URL dans la boîte de dialogue'

    return render(request,'statistics.html',{'error_msg_url':error_msg_url})

