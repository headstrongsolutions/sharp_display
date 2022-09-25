import os
import sys
from time import sleep
from datetime import datetime, timezone, timedelta
from events import Events

## We'll try to use the local caldav library, not the system-installed
sys.path.insert(0, '..')
sys.path.insert(0, '.')

import caldav


class CalDav_Calendar:
    def __init__(self):
        self.events = []
        self.get_attempt = 0

        if os.environ.get('CALENDARURL') is None:
            raise EnvironmentError(f'Failed because CALENDARURL envar is not set')
        self.caldav_url = os.environ.get('CALENDARURL')

        if os.environ.get('CALENDARUSERNAME') is None:
            raise EnvironmentError(f'Failed because CALENDARUSERNAME envar is not set')
        self.caldav_username = os.environ.get('CALENDARUSERNAME')

        if os.environ.get('CALENDARPASSWORD') is None:
            raise EnvironmentError(f'Failed because CALENDARPASSWORD envar is not set')
        self.caldav_password = os.environ.get('CALENDARPASSWORD')

        self.calendar = None
        self.month_events = None
        self.get_calendar()

    def get_calendar(self):
        with caldav.DAVClient(  url=self.caldav_url, 
                                username=self.caldav_username, 
                                password=self.caldav_password
                            ) as client:
            my_principal = client.principal()
            self.calendars = my_principal.calendars()
            self.get_attempt += 1

        if self.calendars is None and self.get_attempt < 10:
            sleep(1)
            self.get_calendar()
        else:
            self.get_attempt = 0
            self.calendar = self.calendars[0]

        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        then = week_start + timedelta(30)

        events = Events(week_start, then) 
        self.month_events = self.calendar.date_search(start=week_start, end=then)

        for event_collection in self.month_events:
            summary = ""
            start = None
            end = None
            duration = ""
            event = {'SUMMARY':'', 'DESCRIPTION':'', 'DTSTART':'', 'DTEND':'', 'DURATION':''}
            for event_list in event_collection.icalendar_instance.subcomponents:
                for event_item in event_list:
                    if event_item in event:
                        event[event_item] = event_list[event_item]
            if 'SUMMARY' in event:
                summary = event['SUMMARY']
            if not summary and 'DESCRIPTION' in event:
                summary = event['DESCRIPTION']
            if 'DTSTART' in event:
                start = event['DTSTART'].dt
            if 'DTEND' in event:
                end = event['DTEND'].dt
            if 'DURATION' in event:
                duration = event['DURATION']
            if start and end:
                end_dt = end
            elif start and duration: 
                end_dt = start + duration.dt
            
            #if start and end_dt:
            events.add_event(start=start, end=end_dt, title=summary, description=None)
        self.events = events

    def print_events(self):
        if len(self.events.events) > 0:
            for event in self.events.events:
                duration = ""
                if event.start is not None and event.end is not None and event.start != event.end:
                    if isinstance(event.start, datetime):
                        starttime = event.start.strftime("%H:%M")
                    if isinstance(event.end, datetime):
                        endtime = event.end.strftime("%H:%M")
                    if starttime != endtime:
                        duration  = (f"({starttime} - {endtime})") 
                print(f"{event.title}: {Events.get_day_from_dt(event, event.start)} {duration}")

if __name__ == "__main__":

    caldav = CalDav_Calendar()
    caldav.print_events()
