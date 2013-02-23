# -*- coding: utf-8 -*-

class ApiInterface(object):
    """This will be the basis for the shared API interfaces once the Ajax and
    Web APIs have been implemented
    """

    @property
    def logged_in(self):
        """Check if a user has been logged in through the API
        """
        raise NotImplemented
