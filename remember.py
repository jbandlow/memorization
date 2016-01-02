import argparse
import memorylib

description = ('A command line tool to add a bunch of reminders'
    ' to Google calendar.  Reminders are set for 10 minutes, 1 & 5 hours,'
    ' 5 & 25 days, 4 months and 2 years')
parser = argparse.ArgumentParser(description=description)
parser.add_argument('text', type=str, help='Thing to remember')
parser.add_argument('--name', type=str, help='Calendar subject line, '
    '(default: "Memory reminder")', default='Memory reminder')
parser.add_argument('--start', type=str, help='Parseable datetime to start reminders'
    ' (default: now)')

def main():
  """Inserts event
  """
  service = memorylib.get_calendar_service()
  # TODO: Add arguments
  flags = parser.parse_args()
  event_list = memorylib.create_reminder_list(
      start_time=flags.start,
      text=flags.text,
      summary=flags.name)

  for event_data in event_list:
    service.events().insert(calendarId='primary', body=event_data).execute()
  print 'Reminders created'

if __name__ == '__main__':
    main()
