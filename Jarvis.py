#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*-
#
# Copyright (C)        : 2021 Headstrong Solutions
# Author:              : Chris Morse <chris@headstrong.solutions>
#
# Name                 : Jarvis integrations

"""Jarvis module"""

import os
import requests
import datetime
import json

class Jarvis:
    def __init__(self):
        if os.environ.get('JARVIS_TEMPS_URL') is None:
            raise EnvironmentError(f'Failed because JARVIS_TEMPS_URL envar is not set')
        self.temps_url = os.environ.get('JARVIS_TEMPS_URL')
        self.latest_temperature = 0
        self.next_access = datetime.datetime.now() 

    def get_temps(self):
        try:
            current_time = datetime.datetime.now()
            if self.next_access < current_time:
                response = requests.get(self.temps_url)
                response.raise_for_status()
                jsonResponse = response.json()
                self.latest_temperature = jsonResponse[0]['Value']
                self.next_access = current_time + datetime.timedelta(minutes=5)

        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return self.latest_temperature
