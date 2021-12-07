#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*-
#
# Copyright (C)        : 2021 Headstrong Solutions
# Author:              : Chris Morse <chris@headstrong.solutions>
#
# Name                 : Sharp Display Clock
# Description          : Sharp Display (2.7" 400X240) Clock
#                      : Weather font credit to https://github.com/isneezy/open-weather-icons 

"""SharpDisplayClock module"""

import os, sys
import board
import busio
import digitalio
import arrow
from PIL import Image, ImageDraw, ImageFont

import adafruit_sharpmemorydisplay
from datetime import datetime
from datetime import timedelta
from threading import Timer

import OpenWeather
import Jarvis

class InfiniteTimer():
    """A Timer class that does not stop, unless you want it to."""
    def __init__(self, seconds, target):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        if self._should_continue:
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()
        else:
            print("Timer already started or running, please wait if you're restarting.")

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False
            self.thread.cancel()
        else:
            print("Timer never started or failed to initialize.")


class SharpDisplayClock:
    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 240
    BLACK = 0
    WHITE = 255
    BORDER = 5
    RGB_WHITE = (255,255,255)
    RGB_BLACK = (0,0,0)
    WEATHER_FONTSIZE = 40
    TINY_FONTSIZE = 12
    SMALL_FONTSIZE = 15
    NORMAL_FONTSIZE = 20
    BIG_FONTSIZE = 40
    LARGE_FONTSIZE = 100
    MASSIVE_FONTSIZE = 160
    MONO_PALETTE = "1"
    CLOCK_LEFT = -6
    CLOCK_MINUTES_LEFT = 150
    CLOCK_TOP = -34

    def __init__(self, timeout_delay: float=1):
        self.openWeather = OpenWeather.OpenWeather()
        self.jarvis = Jarvis.Jarvis()
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI)
        self.scs = digitalio.DigitalInOut(board.D4)
        self.display = adafruit_sharpmemorydisplay.SharpMemoryDisplay(self.spi, self.scs, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.log_timer = None
        self.logging_interval = timeout_delay
        self.run = True
        self.tiny_text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", self.TINY_FONTSIZE)
        self.text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", self.SMALL_FONTSIZE)
        self.large_text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.NORMAL_FONTSIZE)
        self.clock_font = ImageFont.truetype("/usr/share/fonts/truetype/Gothic725/Got725Bd.ttf", self.MASSIVE_FONTSIZE)
        self.weather_font = ImageFont.truetype("/usr/share/fonts/truetype/isneezy_WeatherIcons/isneezy_WeatherIcons.ttf", self.WEATHER_FONTSIZE)
        self.bg_color = self.BLACK
        self.font_color = self.WHITE

        self.rgb_font_color = self.RGB_WHITE
        if self.font_color == self.BLACK:
            self.rgb_font_color = self.RGB_BLACK

        self.rgb_bg_color = self.RGB_WHITE
        if self.bg_color == self.BLACK:
            self.rgb_font_color = self.RGB_BLACK

        self.display_dots = True

        self.clear_screen()

        self.timer = InfiniteTimer(self.logging_interval, self.update_clock)
        self.timer.start()

    def clear_screen(self):
        self.display.fill(self.bg_color)
        self.display.show()

    def seconds_length(self, seconds: float):
        length = 0
        seconds_dec = 0
        if seconds > 0:
            seconds_dec = (seconds / 60)
        length = (seconds_dec * (self.SCREEN_WIDTH / 100)) * 100
        return length

    def update_clock(self):
        image = Image.new(self.MONO_PALETTE, (self.display.width, self.display.height), self.bg_color)
        draw = ImageDraw.Draw(image)
        if self.display_dots:
            draw.ellipse((self.CLOCK_MINUTES_LEFT -5 + 0, 27, self.CLOCK_MINUTES_LEFT -5 + 15, 42), fill=self.font_color, outline=self.bg_color)
            draw.ellipse((self.CLOCK_MINUTES_LEFT -5 + 0, 67, self.CLOCK_MINUTES_LEFT -5 + 15, 82), fill=self.font_color, outline=self.bg_color)
            self.display_dots = False
        else:
            self.display_dots = True

        current_time = datetime.now()
        hours = f'{current_time.strftime("%-I")}'
        minutes = f'{current_time.strftime("%M")}'
        am_pm = 'am'
        friendly_date = f'{current_time.strftime("%A")}, {arrow.get(current_time).format("Do")} of {current_time.strftime("%B")}, {current_time.strftime("%Y")}'
        if current_time.strftime("%p") == "PM":
            am_pm = 'pm'
        hours_size_w, hours_size_h = self.clock_font.getsize(hours)
        friendly_date_size_w, friendly_date_size_h = self.text_font.getsize(friendly_date)

        draw.text(
            (self.CLOCK_MINUTES_LEFT - hours_size_w, self.CLOCK_TOP),
            hours,
            font=self.clock_font,
            fill=self.font_color
        )

        draw.text(
            (self.CLOCK_LEFT + self.CLOCK_MINUTES_LEFT + 16, self.CLOCK_TOP),
            minutes,
            font=self.clock_font,
            fill=self.font_color
        )

        latest_temp = self.jarvis.get_temps()
        draw.text(
            (self.SCREEN_WIDTH - 40, 0),
            f'{latest_temp}°C',
            font=self.tiny_text_font,
            fill=self.font_color
        )

        draw.text(
            (self.SCREEN_WIDTH - 40, 92),
            am_pm,
            font=self.text_font,
            fill=self.font_color
        )

        draw.rectangle(
            (0, 125, self.seconds_length(int(current_time.strftime('%-S'))), 127),
            fill=self.font_color
        )

        draw.text(
            (((self.SCREEN_WIDTH / 2) - (friendly_date_size_w / 2)) / 2, 130),
            friendly_date,
            font=self.large_text_font,
            fill=self.font_color
        )

        ## Weather information from OpenWeather module
        self.openWeather.get_report(OpenWeather.WeatherReport.Daily, from_file=False)
        weather_left = 0
        for report in self.openWeather.daily_reports:
            draw.text(
                (weather_left, 160),
                report.weather.unicode_icon,
                font=self.weather_font,
                fill=self.font_color
            )
            draw.text(
                (weather_left, 200),
                report.friendly_day,
                font=self.text_font,
                fill=self.font_color
            )
            draw.text(
                (weather_left, 220),
                f'{round(report.feels_like.day_c)}°C',
                font=self.text_font,
                fill=self.font_color
            )
            if weather_left < 400:
                weather_left += 60
            else:
                weather_left = 0
        
        self.display.image(image)
        self.display.show()

if __name__ == "__main__":
    try:
        sharpDisplayClock = SharpDisplayClock(timeout_delay=1)
    except KeyboardInterrupt:
        print('Quitting SharpDisplayClock')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
