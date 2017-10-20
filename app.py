# -*- coding: utf-8 -*-

from os import path
from loader import Configuration


with Configuration('etc/config.json') as config:

    from fanstatic import Fanstatic
    from rutter.urlmap import URLMap
    from uvc.concierge import wrapper
    from uvc.concierge.portals import XMLRPCPortal
    from uvc.concierge.websockets.app import handle
    from uvc.concierge.websockets.websocket import WebSocketWSGI
    from uvc.concierge.login import logout_app, login_center
    from wsgicors import CORS
    from wsgiproxy import HostProxy
    from repoze.who.config import make_middleware_with_config
    
    # portals
    href = (
        "http://karl.novareto.de:7080/VirtualHostBase/http/" +
        "karl.novareto.de:8000/plone/Plone/VirtualHostRoot/_vh_plone")
    plone = HostProxy(href, client='urllib3')
    plone.login_url = "http://karl.novareto.de:7080/Plone/"
    plone.string_keys = ['REMOTE_USER',]
    plone.use_x_headers = True

    href = 'http://karl.novareto.de:8090/app/++vh++http:karl.novareto.de:8000/uvcsite/++'
    uvcsite = HostProxy(href, client="urllib3")
    uvcsite.login_url = "http://karl.novareto.de:8090/app/"
    uvcsite.string_keys = ['REMOTE_USER',]
    uvcsite.use_x_headers = True
    
    # The application.
    mapping = URLMap()
    mapping['/plone'] = wrapper(mapping, plone)
    mapping['/uvcsite'] = wrapper(mapping, uvcsite)
    mapping['/socket'] = WebSocketWSGI(mapping, handle)
    mapping['/socket/'] = WebSocketWSGI(mapping, handle)
    mapping['/login'] = login_center(mapping)
    mapping['/logout'] = logout_app

    # Middlewares wrapping
    application = make_middleware_with_config(
        mapping, {'here': path.dirname(__file__)},
        config_file=config['who']['config'],
        log_file="stdout",
        log_level="info",
        )

    application = CORS(
        application,
        headers="*",
        methods="*",
        maxage="180",
        origin="*",
        credentials="true",
    )

    application = Fanstatic(application, publisher_signature="fs_concierge")

    print(application, "Application is ready.")
