#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*-
#
# Copyright (C)        : 2021 Headstrong Solutions
# Author:              : Chris Morse <chris@headstrong.solutions>
#
# Name                 : Open Weather

"""OpenWeather module"""
from enum import Enum
import os
import requests
import json
import datetime
from dataclasses import dataclass
from typing import List

@dataclass 
class WeatherDescriptionObject:
    id: int
    main: str
    description: str
    icon: str
    unicode_icon: str

@dataclass
class HourlyWeatherObject:
    dt: int
    friendly_time: str
    friendly_day: str
    temp: float
    temp_c: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: int
    clouds: int
    visibility: int
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: List[WeatherDescriptionObject]
    pop: int

@dataclass
class DailyWeatherTempsObject:
    day: float
    day_c:float
    min: float
    max: float
    night: float
    eve: float
    morn: float

@dataclass
class DailyWeatherObject:
    dt: int
    friendly_day: str
    sunrise: int
    sunset: int
    moonrise: int
    moonset: int
    moon_phase: int
    temp: DailyWeatherTempsObject
    feels_like: DailyWeatherTempsObject
    pressure: int
    humidity: int
    dew_point: float
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: List[WeatherDescriptionObject]
    clouds: int
    pop: int
    uvi: float

class WeatherReport(Enum):
    Hourly = 0
    Daily = 1

class OpenWeather:

    def __init__(self):
        if os.environ.get('OPENWEATHER') is None:
            raise EnvironmentError(f'Failed because OPENWEATHER envar is not set')
        self.api_key = os.environ.get('OPENWEATHER')
        if os.environ.get('MYLOCATIONLONG') is None:
            raise EnvironmentError(f'Failed because MYLOCATIONLONG envar is not set')
        self.location_long = os.environ.get('MYLOCATIONLONG')
        if os.environ.get('MYLOCATIONLAT') is None:
            raise EnvironmentError(f'Failed because MYLOCATIONLAT envar is not set')
        self.location_lat = os.environ.get('MYLOCATIONLAT')
        self.part = None
        self.base_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={self.location_lat}&lon={self.location_long}&exclude={self.part}&appid={self.api_key}'
        self.filepath = "weather_report.json"
        self.weather_reports = []
        self.hourly_reports = []
        self.daily_reports = []
        self.next_access = datetime.datetime.now() 

    def convert_from_icon_to_unicode(self, icon):
        icons = {}
        icons['01d'] = "\uea02"
        icons['01n'] = "\uea01"
        icons['02d'] = "\uea03"
        icons['02n'] = "\uea04"
        icons['03d'] = "\uea05"
        icons['03n'] = "\uea06"
        icons['04d'] = "\uea07"
        icons['04n'] = "\uea08"
        icons['09d'] = "\uea09"
        icons['09n'] = "\uea0a"
        icons['10d'] = "\uea0b"
        icons['10n'] = "\uea0c"
        icons['11d'] = "\uea0d"
        icons['11n'] = "\uea0e"
        icons['1232n'] = "\uea0f"
        icons['13d'] = "\uea10"
        icons['13n'] = "\uea11"
        icons['50d'] = "\uea12"
        icons['50n'] = "\uea13"
        return icons[icon]

    def convert_from_f_to_c(self, f_temp:float):
        c_temp = (f_temp-32) * .5556
        return c_temp

    def convert_from_k_to_c(self, k_temp:float):
        c_temp = k_temp-273.15
        return c_temp

    def convert_dt_to_datetime(self, dt: str):
        return datetime.datetime.utcfromtimestamp(dt)

    def create_hourly_reports(self):
        self.hourly_reports = []
        for raw_weather in self.weather_reports['hourly']:
            hourlyWeatherDescriptionObject = WeatherDescriptionObject(
                raw_weather['weather'][0]['id'], 
                raw_weather['weather'][0]['main'], 
                raw_weather['weather'][0]['description'], 
                raw_weather['weather'][0]['icon']
            )

            weather_datetime = self.convert_dt_to_datetime(raw_weather['dt'])
            friendly_time = f'{weather_datetime.strftime("%-I")}{weather_datetime.strftime("%p").lower()}' 
            friendly_day = f'{weather_datetime.strftime("%a").upper()}' 
            hourlyWeatherObject = HourlyWeatherObject(
                raw_weather['dt'],
                friendly_time,
                friendly_day,
                raw_weather['temp'],
                self.convert_from_k_to_c(raw_weather['temp']),
                raw_weather['feels_like'],
                raw_weather['pressure'],
                raw_weather['humidity'],
                raw_weather['dew_point'],
                raw_weather['uvi'],
                raw_weather['clouds'],
                raw_weather['visibility'],
                raw_weather['wind_speed'],
                raw_weather['wind_deg'],
                raw_weather['wind_gust'],
                hourlyWeatherDescriptionObject,
                raw_weather['pop']
            )
            self.hourly_reports.append(hourlyWeatherObject)
        return self.hourly_reports

    def create_daily_reports(self):
        self.daily_reports = []
        for raw_weather in self.weather_reports['daily']:
            temp = DailyWeatherTempsObject(
                raw_weather['temp']['day'],
                self.convert_from_k_to_c(raw_weather['temp']['day']),
                raw_weather['temp']['min'],
                raw_weather['temp']['max'],
                raw_weather['temp']['night'],
                raw_weather['temp']['eve'],
                raw_weather['temp']['morn']
            )
            feels_like = DailyWeatherTempsObject(
                raw_weather['feels_like']['day'],
                self.convert_from_k_to_c(raw_weather['temp']['day']),
                None,
                None,
                raw_weather['feels_like']['night'],
                raw_weather['feels_like']['eve'],
                raw_weather['feels_like']['morn']
            )
            unicode_icon = self.convert_from_icon_to_unicode(raw_weather["weather"][0]["icon"])
            weather = WeatherDescriptionObject(
                raw_weather['weather'][0]['id'], 
                raw_weather['weather'][0]['main'], 
                raw_weather['weather'][0]['description'], 
                raw_weather['weather'][0]['icon'],
                unicode_icon
            )
            weather_datetime = self.convert_dt_to_datetime(raw_weather['dt'])
            report = DailyWeatherObject(
                raw_weather['dt'],
                f'{weather_datetime.strftime("%a").upper()}',
                raw_weather['sunrise'],
                raw_weather['sunset'],
                raw_weather['moonrise'],
                raw_weather['moonset'],
                raw_weather['moon_phase'],
                temp,
                feels_like,
                raw_weather['pressure'],
                raw_weather['humidity'],
                raw_weather['dew_point'],
                raw_weather['wind_speed'],
                raw_weather['wind_deg'],
                raw_weather['wind_gust'],
                weather,
                raw_weather['clouds'],
                raw_weather['pop'],
                raw_weather['uvi'],
            )

            self.daily_reports.append(report)
        return self.daily_reports

    def get_weather_data(self):
        weather_reports = []
        response = requests.get(self.base_url)
        weather_reports = response.json()
        self.weather_reports = weather_reports

    def save_weather_data_to_file(self, weather_reports):
        with open(self.filepath, "w") as file_write:
            json.dump(weather_reports, file_write)
                
    def load_weather_data_from_file(self):
        json_file_object = open(self.filepath)
        weather_report = json.load(json_file_object)
        self.weather_reports = weather_report

    def get_report(self, report_type: WeatherReport, from_file: bool=True):
        current_time = datetime.datetime.now()
        if self.next_access < current_time and from_file is False:
            print('Getting live data from OpenWeatherMap')
            self.get_weather_data()
            self.save_weather_data_to_file(self.weather_reports)
            self.next_access = current_time + datetime.timedelta(hours=1)
        elif len(self.weather_reports) < 1:
            print('Loading data from file')
            self.load_weather_data_from_file()

        if report_type == WeatherReport.Daily:
            return self.create_daily_reports()

        elif report_type == WeatherReport.Hourly:  
            return self.create_hourly_reports()  

