# -*- coding: utf-8 -*-

import requests

from ..api import ApiInterface
from ..constants import AJAX
from .errors import *

class AjaxApi(ApiInterface):
    """AJAX call API
    """

    METHOD_POST = 'POST'
    METHOD_GET  = 'GET'

    def __init__(self):
        self._connector = requests.Session()

    def start_session(self):
        pass

    def user_login(self):
        pass

    def videoPlayer_getStandardConfig(self):
        pass

    def videoPlayer_getChromelessConfig(self):
        pass
