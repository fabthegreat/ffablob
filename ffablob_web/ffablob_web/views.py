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

def main(request):
        race_1 = design.Race('184050','30+Km')
        race_1.extract_runners_from_race()

        return render(request,'statistics.html',{'results':race_1.results})

