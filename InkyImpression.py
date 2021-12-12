#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*-
#
# Copyright (C)        : 2021 Headstrong Solutions
# Author:              : Chris Morse <chris@headstrong.solutions>
#
# Name                 : Inky Impression

from typing import Callable
import RPi.GPIO as GPIO

class InkyImpression:
    def __init__(self, button1_function: Callable, button2_function: Callable, button3_function: Callable, button4_function: Callable):
        self.BUTTONS = {5:button1_function, 6:button2_function, 16:button3_function, 24:button4_function}
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(list(self.BUTTONS.keys()), GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def bind_button_events(self):
        for pin, fn in self.BUTTONS.items():
            GPIO.add_event_detect(pin, GPIO.FALLING, fn, bouncetime=250)

    def handle_button(self, pin):
        label = self.LABELS[self.BUTTONS.index(pin)]
        print(f"Button press detected on pin: {pin}")
