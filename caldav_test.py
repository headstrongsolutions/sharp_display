import caldav

class CalDavCalendar:
    def __init__(self):

    if os.environ.get('CALENDARURL') is None:
                raise EnvironmentError(f'Failed because OPENWEATHER envar is not set')
            self.caldav_url = os.environ.get('CALENDARURL')

    if os.environ.get('CALENDARUSERNAME') is None:
                raise EnvironmentError(f'Failed because OPENWEATHER envar is not set')
            self.caldav_username = os.environ.get('CALENDARUSERNAME')

    if os.environ.get('CALENDARPASSWORD') is None:
                raise EnvironmentError(f'Failed because OPENWEATHER envar is not set')
            self.caldav_password = os.environ.get('CALENDARPASSWORD')

    def get_calendar(self):
        with caldav.DAVClient(  url=caldav_url, 
                                username=caldav_username, 
                                password=caldav_password
                            ) as client:
            my_principal = client.principal()
            self.calendars = my_principal.calendars()

        print(repr(self.calendars))