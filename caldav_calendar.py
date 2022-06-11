import os
import sys
from datetime import datetime, date, timedelta
from events import Events

## We'll try to use the local caldav library, not the system-installed
sys.path.insert(0, '..')
sys.path.insert(0, '.')

import caldav


class CalDav_Calendar:
    def __init__(self):
        self.events = []

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

        self.calendar = self.calendars[0]
        if self.calendar is None:
            self.get_calendar()
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        then = week_start + timedelta(30)

        events = Events(week_start, then) 

        self.month_events = self.calendar.date_search(week_start, then)

        for event in self.month_events:
            summary = event.icalendar_instance.subcomponents[0]['SUMMARY']
            day = event.icalendar_instance.subcomponents[0]['DTSTART'].dt.day
            month = event.icalendar_instance.subcomponents[0]['DTSTART'].dt.month
            year = event.icalendar_instance.subcomponents[0]['DTSTART'].dt.year
            start = event.icalendar_instance.subcomponents[0]['DTSTART'].dt
            duration = event.icalendar_instance.subcomponents[0]['DURATION']

            start_dt = start
            if start and duration: 
                end_dt = start + duration.dt
            
            if start_dt and end_dt:
                events.add_event(start=start_dt, end=end_dt, title=summary, description=None)
        self.events = events

    def print_events(self):
        if len(self.events.events) > 0:
            for event in self.events.events:
                duration = ""
                if event.start is not None and event.end is not None and event.start != event.end:
                    starttime = event.start.strftime("%H:%M")
                    endtime = event.end.strftime("%H:%M")
                    if starttime != endtime:
                        duration  = (f"({starttime} - {endtime})") 
                print(f"{event.title}: {Events.get_day_from_dt(event, event.start)} {duration}")
