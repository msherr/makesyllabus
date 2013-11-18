#!/usr/bin/python

# A syllabus creator by Micah Sherr
# Georgetown University
# msherr@cs.georgetown.edu
#
# Use at your own risk.
# Released under GPLv3


import dateutil.parser
from dateutil.tz import *
import argparse
import datetime
import yaml
from jinja2 import Template
from icalendar import Calendar, Event
import pytz


def parse_command_line():
    parser = argparse.ArgumentParser(description='Syllabus generator')
    parser.add_argument('--holidays', help='list of holidays, separated by ":"; use # to define ranges')
    parser.add_argument('--start', help='start date', required=True)
    parser.add_argument('--end', help='end date', required=True)
    parser.add_argument('--days', help='days of week (0-6, where Monday is 0 and Sunday is 0)', required=True)
    parser.add_argument('--schedule', help='schedule file', required=True)
    parser.add_argument('--template', help='django template file (must specify either this or --ical')
    parser.add_argument('--ical', help='icalendar output file (must specify either this or --template')
    parser.add_argument('--header', help='header file to insert before template')
    parser.add_argument('--footer', help='footer file to insert after template')
    parser.add_argument('--starttime', help='the time at which the class begins; useful for iCalendar output')
    parser.add_argument('--endtime', help='the time at which the class ends; useful for iCalendar output')
    parser.add_argument('--course', help='some identifier which will precede the summary in iCalendar output')
    args = parser.parse_args()

    # deal with conditional dependencies
    if args.ical is None and args.template is None:
        print "ERROR: must specify either --ical or --template"
        exit(1)
    if args.ical is not None and (args.starttime is None or args.endtime is None):
        print "ERROR: for calendars, you must specify start and end times"
        exit(1)        
    return args


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + datetime.timedelta(n)

        
def parse_holidays( holiday_string ):
    holidays = list()
    parts = holiday_string.split(":")
    for part in parts:
        if '#' in part:
            (begin,end) = part.split("#")
            begin = dateutil.parser.parse(begin).date()
            end = dateutil.parser.parse(end).date()
            for single_date in daterange(begin,end):
                holidays.append(single_date)
        else:
            day = dateutil.parser.parse(part).date()
            holidays.append(day)
    return holidays



def make_ical_event(class_date,start_time,end_time,class_info,args):
    event = Event()
    if args.course is None:
        event.add('summary', class_info['description'])
    else:
        event.add('summary', args.course + ": " + class_info['description'])
    event.add('dtstart', datetime.datetime(class_date.year,class_date.month,class_date.day,start_time.hour,start_time.minute,start_time.second,tzinfo=tzlocal()) )
    event.add('dtstamp', datetime.datetime(class_date.year,class_date.month,class_date.day,start_time.hour,start_time.minute,start_time.second, tzinfo=tzlocal()) )
    event.add('dtend', datetime.datetime(class_date.year,class_date.month,class_date.day,end_time.hour,end_time.minute,end_time.second, tzinfo=tzlocal()) )
    event['uid'] = str(class_date.year)+str(class_date.month)+str(class_date.day)+"T"+start_time.strftime("%H%M%S")+"Z@security.cs.georgetown.edu"
    if 'readings' in class_info:
        desc = 'Readings:\n'
        for reading in class_info['readings']:
            desc += "   " + reading['title'] + "\n"
            if 'url' in reading:
                event.add('url', reading['url'])
        event.add('description', desc )
    return event
    


def main():
    args = parse_command_line()
    start = dateutil.parser.parse(args.start).date()
    end = dateutil.parser.parse(args.end).date()
    days = list(args.days)

    with file(args.schedule, 'rt') as f:
        schedule = yaml.load(f)
    if args.template is not None:
        with open(args.template,'rt') as f:
            t = Template(f.read())
    if args.ical is not None:
        cal = Calendar()
        cal.add('prodid', '-//MicahSherr@Georgetown//make-syllabus//')
        cal.add('version', '2.0')
        
    holidays = parse_holidays( args.holidays )

    if args.template is not None and args.header is not None:
        with open(args.header,'rt') as h:
            print h.read()

    if args.starttime is not None and args.endtime is not None:
        st = dateutil.parser.parse(args.starttime).time()
        et = dateutil.parser.parse(args.endtime).time()
            
    day_count = (end - start).days + 1
    class_num = 0
    for single_date in (start + datetime.timedelta(n) for n in range(day_count)):
        class_info = dict()
        day_of_week = str(single_date.weekday())
        if day_of_week in days:
            if single_date in holidays:
                class_info['lec_num'] = "-"
                class_info['lec_date'] = single_date
                class_info['description'] = 'No class'
                class_info['noclass'] = True
            else:
                # not a holiday; we have class.
                if class_num < len(schedule):
                    class_info = schedule[class_num]
                class_num = class_num + 1
                class_info['lec_num'] = class_num
                class_info['lec_date'] = single_date
                
            if args.template is not None:
                print t.render(class_info)
            if args.ical is not None and single_date not in holidays:
                event = make_ical_event(single_date,st,et,class_info,args)
                cal.add_component(event)

    if args.template is not None and args.footer is not None:
        with open(args.footer,'rt') as f:
            print f.read()

    if args.ical is not None:
        with open(args.ical,'wb') as o:
            o.write(cal.to_ical())
            

if __name__ == "__main__":
    main()
