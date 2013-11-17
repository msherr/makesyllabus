#!/usr/bin/python

# A syllabus creator by Micah Sherr
# Georgetown University
# msherr@cs.georgetown.edu
#
# Use at your own risk.
# Released under GPLv3


import dateutil.parser
import argparse
import datetime
import yaml
from jinja2 import Template
import pytz


def parse_command_line():
    parser = argparse.ArgumentParser(description='Syllabus generator')
    parser.add_argument('--holidays', help='list of holidays, separated by ":"; use # to define ranges')
    parser.add_argument('--start', help='start date', required=True)
    parser.add_argument('--end', help='end date', required=True)
    parser.add_argument('--days', help='days of week (0-6, where Monday is 0 and Sunday is 0)', required=True)
    parser.add_argument('--schedule', help='schedule file', required=True)
    parser.add_argument('--template', help='django template file', required=True)
    parser.add_argument('--header', help='header file to insert before template')
    parser.add_argument('--footer', help='footer file to insert after template')
    parser.add_argument('--starttime', help='the time at which the class begins; useful for iCalendar output')
    parser.add_argument('--endtime', help='the time at which the class ends; useful for iCalendar output')
    args = parser.parse_args()
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
    


def main():
    args = parse_command_line()
    start = dateutil.parser.parse(args.start).date()
    end = dateutil.parser.parse(args.end).date()
    days = list(args.days)

    with file(args.schedule, 'rt') as f:
        schedule = yaml.load(f)
    with open(args.template,'rt') as f:
        t = Template(f.read())

    holidays = parse_holidays( args.holidays )

    if args.header is not None:
        with open(args.header,'rt') as h:
            print h.read()

    if args.starttime is not None and args.endtime is not None:
        st = dateutil.parser.parse(args.starttime).time()
        et = dateutil.parser.parse(args.endtime).time()
    else:
        st = None
        et = None    
            
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
                
                if st != None and et != None:
                    class_info['date_begin'] = str(single_date.year)+str(single_date.month)+str(single_date.day)+"T"+st.strftime("%H%M%S")+"Z"
                    class_info['date_end'] = str(single_date.year)+str(single_date.month)+str(single_date.day)+"T"+et.strftime("%H%M%S")+"Z"
                
            print t.render(class_info)

    if args.footer is not None:
        with open(args.footer,'rt') as f:
            print f.read()


if __name__ == "__main__":
    main()
