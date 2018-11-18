"""ffablob_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path,re_path
from django.contrib import admin

from ffablob_web.views import main,flush_cart,load_race,remove_race,show_race,load_analysis,csv_export,convert,compare,search,add_race,reload_race,check

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    path('flushcart/', flush_cart),
    path('removerace/<race_ID>/<race_type>', remove_race),
    path('loadrace/', load_race),
    path('convert/', convert),
    path('check/', check),
    path('compare/', compare),
    path('search/<sort_key>', search),
    path('reloadrace/<race_ID>/<race_type>', reload_race),
    path('csvexport/<race_ID>/<race_type>', csv_export),
    path('showrace/<race_ID>/<race_type>', show_race),
    path('loadanalysis/<race_ID>/<race_type>/', load_analysis),
    path('addrace/<race_ID>/<race_type>', add_race),
    re_path(r'^$', main),
]
