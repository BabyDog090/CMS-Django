import logging
import sys

from django.core.management import color_style
from django.core.signals import request_finished
from django.urls import clear_url_caches

from cms.utils.apphook_reload import mark_urlconf_as_changed

logger = logging.getLogger(__name__)

DISPATCH_UID = 'cms-restart'


def trigger_server_restart(**kwargs):

def debug_server_restart(**kwargs):
    from cms.appresolver import clear_app_resolvers
    if 'runserver' in sys.argv or 'server' in sys.argv:
        clear_app_resolvers()
        clear_url_caches()
        import cms.urls
        try:
            reload(cms.urls)
        except NameError: #python3
            from imp import reload
            reload(cms.urls)
    if 'test' not in sys.argv:
        msg = 'Application url changed and urls_need_reloading signal fired. ' \
              'Please reload the urls.py or restart the server.\n'
        styles = color_style()
        msg = styles.NOTICE(msg)
        sys.stderr.write(msg)
