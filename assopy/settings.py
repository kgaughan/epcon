# -*- coding: UTF-8 -*-
from django.conf import settings

if hasattr(settings, 'ASSOPY_JANRAIN'):
    JANRAIN = {
        'domain': settings.ASSOPY_JANRAIN['domain'],
        'app_id': settings.ASSOPY_JANRAIN['app_id'],
        'secret': settings.ASSOPY_JANRAIN['secret'],
    }
else:
    JANRAIN = None

BACKEND = 'http://assopy.pycon.it/conference/externalcall'

SEARCH_MISSING_USERS_ON_BACKEND = getattr(settings, 'ASSOPY_SEARCH_MISSING_USERS_ON_BACKEND', False)

TICKET_PAGE = getattr(settings, 'ASSOPY_TICKET_PAGE', None)

SEND_EMAIL_TO = getattr(settings, 'ASSOPY_SEND_EMAIL_TO', None)

VIES_WSDL_URL = 'http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'
