"""
WSGI config for ffablob_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import site
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ffablob_web.settings")
site.addsitedir('/home/ftg/.local/lib/python2.7/site-packages')

application = get_wsgi_application()
