import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import dateutil.parser
import datetime
import pytz

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Memory Helper'
DEFAULT_TIME_ZONE = 'America/Los_Angeles'
DEFAULT_SUMMARY = 'Reminder event'
DEFAULT_EVENT_DURATION = datetime.timedelta(minutes=5)
DEFAULT_TZ = pytz.timezone(DEFAULT_TIME_ZONE)
DEFAULT_REMINDER_HOUR = 8
DEFAULT_REMINDER_MINUTE = 0
DEFAULT_TIME_DELTAS = [
    datetime.timedelta(minutes=10),
    datetime.timedelta(hours=1),
    datetime.timedelta(hours=5),
    datetime.timedelta(days=1),
    datetime.timedelta(days=5),
    datetime.timedelta(days=25),
    datetime.timedelta(days=122),
    datetime.timedelta(days=730)]



def _create_reminder_event(start_time, **kwargs):
  """Private function to create a reminder JSON blob.

  It is the callers responsibility to make sure the arguments are correct.
  """
  event = {
    'summary': kwargs['summary'],
    'description': kwargs['description'],
    'start': {
      'dateTime': start_time.isoformat(),
      'timeZone': kwargs['time_zone'],
    },
    'end': {
      'dateTime': (start_time + kwargs['duration']).isoformat(),
      'timeZone': kwargs['time_zone'],
    }
  }
  if kwargs.get('reminder') is not None:
    event['reminders'] = {
      'useDefault': False,
      'overrides': [
        {'method': 'popup', 'minutes': kwargs['reminder']},
      ],
    }
  else:
    event['reminders'] = {'useDefault': True}

  return event

def create_reminder_list(start_time=None,
    text='',
    summary=DEFAULT_SUMMARY,
    reminder_hour=DEFAULT_REMINDER_HOUR,
    reminder_minute=DEFAULT_REMINDER_MINUTE,
    reminder_prewarn=0,
    time_deltas=DEFAULT_TIME_DELTAS,
    time_zone=DEFAULT_TIME_ZONE,
    duration=DEFAULT_EVENT_DURATION):
  """Returns a list of events to create.
  """
  event_kwargs = {
      'summary': summary,
      'duration': duration,
      'description': text,
      'time_zone': time_zone,
      'reminder': reminder_prewarn}

  if not start_time:
    start_time = datetime.datetime.now(DEFAULT_TZ)
  else:
    start_time = DEFAULT_TZ.localize(dateutil.parser.parse(start_time))
  # Events today are precise to the second.
  start_time = start_time.replace(microsecond=0)
  deltas = filter(lambda x: x < datetime.timedelta(days=1), time_deltas)
  reminders = [_create_reminder_event(start_time + delta, **event_kwargs)
    for delta in deltas]

  # Events 1 day or more out are at reminder_hour, reminder_minute
  start_time = start_time.replace(hour=reminder_hour, minute=reminder_minute)
  deltas = filter(lambda x: x >= datetime.timedelta(days=1), time_deltas)
  reminders.extend(_create_reminder_event(start_time + delta, **event_kwargs)
    for delta in deltas)
  return reminders

# TODO: This has too many hard-coded params.
def get_credentials():
  """Gets valid user credentials from storage.

  If nothing has been stored, or if the stored credentials are invalid,
  the OAuth2 flow is completed to obtain the new credentials.

  Returns:
      Credentials, the obtained credential.
  """
  flags = tools.argparser.parse_known_args()[0]
  home_dir = os.path.expanduser('~')
  credential_dir = os.path.join(home_dir, '.credentials')
  if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
  credential_path = os.path.join(credential_dir,
                                 'calendar-python.json')

  store = oauth2client.file.Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    credentials = tools.run_flow(flow, store, flags)
    print('Storing credentials to ' + credential_path)
  return credentials

def get_calendar_service():
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  return discovery.build('calendar', 'v3', http=http)
