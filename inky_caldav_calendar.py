#!/usr/bin/env python3

import os
from datetime import datetime 
from typing import List

from inky.inky_uc8159 import Inky
# To simulate:
#from inky.mock import InkyMockImpression as Inky
from inky.auto import auto

from font_source_sans_pro import SourceSansProLight
from font_source_sans_pro import SourceSansPro
from font_source_sans_pro import SourceSansProSemibold
from PIL import Image, ImageDraw, ImageFont

from events import Events
from caldav_calendar import CalDav_Calendar


class InkyImpression:
    def __init__(self):
        self.inky = Inky()
        self.light_font = ImageFont.truetype(SourceSansProLight, 14)
        self.normal_font = ImageFont.truetype(SourceSansPro, 14)
        self.semibold_font = ImageFont.truetype(SourceSansProSemibold, 14)

        self.BLACK=(0,0,0)
        self.WHITE=(255, 255, 255)
        self.GREEN=(0, 255, 0)
        self.BLUE=(0, 0, 255)
        self.RED=(255, 0, 0)
        self.YELLOW=(255, 255, 0)
        self.ORANGE=(255, 140, 0)
        self.CLEAR=(255, 255, 255)

        self.DESATURATED_PALETTE = [
            (0, 0, 0),
            (255, 255, 255),
            (0, 255, 0),
            (0, 0, 255),
            (255, 0, 0),
            (255, 255, 0),
            (255, 140, 0),
            (255, 255, 255)
        ]

        self.SATURATED_PALETTE = [
            (57, 48, 57),       #   BLACK
            (255, 255, 255),    #   WHITE
            (58, 91, 70),       #   GREEN?
            (61, 59, 94),       #   BLUE?
            (156, 72, 75),      #   YELLOW?
            (208, 190, 71),     #   ORANGE?
            (177, 106, 73),     #   RED?
            (255, 255, 255)     #   CLEAR
        ]

        self.colors = ['Black', 'White', 'Green', 'Blue', 'Red', 'Yellow', 'Orange']

        self.PATH = os.path.dirname(__file__)

        self.img = Image.open(os.path.join(self.PATH, "resources/backdrop.png")).resize(self.inky.resolution)
        self.draw = ImageDraw.Draw(self.img)

    def draw_day_headers(self, box_width:int):
        self.draw.rectangle((1, 1, 600, 20),fill=self.BLUE)
        self.draw.text(((box_width*0)+30,2), "MON", self.WHITE, font=self.semibold_font)
        self.draw.text(((box_width*1)+30,2), "TUE", self.WHITE, font=self.semibold_font)
        self.draw.text(((box_width*2)+30,2), "WED", self.WHITE, font=self.semibold_font)
        self.draw.text(((box_width*3)+30,2), "THU", self.WHITE, font=self.semibold_font)
        self.draw.text(((box_width*4)+30,2), "FRI", self.WHITE, font=self.semibold_font)
        self.draw.text(((box_width*5)+30,2), "SAT", self.WHITE, font=self.semibold_font)
        self.draw.text(((box_width*6)+30,2), "SUN", self.WHITE, font=self.semibold_font)

    def draw_day(self, x:int, y:int, box_width:int, box_height:int, today_string:str, events:List[str], today=False):
        date_box_height = 15
        # draw date background
        colour = self.RED
        if today:

            colour = self.GREEN
        self.draw.rectangle((x, y, x+box_width, y+date_box_height), 
                        fill=colour)
        self.draw.rectangle((x, y+date_box_height, x+box_width, y+box_height), 
                        fill=self.WHITE)

        # write date
        center_start_pos = 0
        if len(today_string) == 6:
            center_start_pos = 22
        elif len(today_string) == 5:
            center_start_pos = 27

        # date header
        self.draw.text((x + center_start_pos, y-2), today_string , self.WHITE, font=self.semibold_font)

        # general y offset
        offset_y = y + (date_box_height -2)

        # event strings
        if len(events) > 0:
            event_y = offset_y
            event_x = x + 2
            event_count = 0
            for event in events:
                if event_count < 20:
                    friendly_time = event.start.strftime("%H:%M")
                    if event.end:
                        friendly_time_end = event.end.strftime("%H:%M")
                        self.draw.text((event_x, event_y), event.title[:13] , self.BLUE, font=self.normal_font)
                        if friendly_time != friendly_time_end:
                            friendly_time = str("%s - %s" % (friendly_time, friendly_time_end))
                            self.draw.text((event_x, event_y+13), friendly_time , self.GREEN, font=self.normal_font)
                            event_y = event_y + 15
                    
                    event_y = event_y + 15
                    event_count = event_count +1

        # draw containing box
        right_edge = x+box_width
        if right_edge > 598:
            right_edge = 598
            
        self.draw.line((x, offset_y, right_edge, offset_y), colour)
        self.draw.line((x, offset_y, x, offset_y+box_height), colour)
        
    def render_caldav_to_inky(self):
        calendar_data = CalDav_Calendar()

        x = 1
        x_max = 600
        y = 21
        y_max = 488
        day_count = 0
        box_width = 86
        box_height = 93
        today = calendar_data.events.get_day_from_dt(datetime.now())
        self.draw_day_headers(box_width)
        for day in calendar_data.events.dates:
            events = calendar_data.events.find_events_by_day(day)

            datetime_day = None
            friendly_day = calendar_data.events.remove_year_from_friendly_date(day)
            if day_count < 28:
                todays_the_day = False
                if today == day:
                    todays_the_day = True
                self.draw_day(x, y, box_width, box_height, friendly_day, events, todays_the_day)
                day_count = day_count + 1
            if x < x_max - 150:
                x = x + box_width
            else:
                x = 1
                y = y + box_height + 15

        # right and bottom edges
        self.draw.line((598,0,598,446), self.RED)
        self.draw.line((0,446,598,446), self.RED)

        self.inky.set_image(self.img, saturation=1)
        self.inky.show()
        # To simulate:
        #inky.wait_for_window_close()
