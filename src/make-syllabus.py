#!/usr/bin/python

# A syllabus creator by Micah Sherr
# Georgetown University
# msherr@cs.georgetown.edu


import dateutil.parser
import argparse
import datetime
import yaml
from jinja2 import Template


def parse_command_line():
    parser = argparse.ArgumentParser(description='Syllabus generator')
    parser.add_argument('--holidays', help='list of holidays, separated by ":"')
    parser.add_argument('--start', help='start date', required=True)
    parser.add_argument('--end', help='end date', required=True)
    parser.add_argument('--days', help='days of week (0-6, where Monday is 0 and Sunday is 0)', required=True)
    parser.add_argument('--schedule', help='schedule file', required=True)
    parser.add_argument('--template', help='django template file', required=True)
    parser.add_argument('--header', help='header file to insert before template')
    parser.add_argument('--footer', help='footer file to insert before template')
    args = parser.parse_args()
    return args



def main():
    args = parse_command_line()
    start = dateutil.parser.parse(args.start).date()
    end = dateutil.parser.parse(args.end).date()
    days = list(args.days)

    default_description = { 'description' : 'TBD' }
    
    with file(args.schedule, 'rt') as f:
        schedule = yaml.load(f)
    with open(args.template,'rt') as f:
        t = Template(f.read())

    if args.holidays is not None:
        holidays = map( lambda x : dateutil.parser.parse(x).date(), args.holidays.split(':'))
    else:
        holidays = []

    if args.header is not None:
        with open(args.header,'rt') as h:
            print h.read()
    
    day_count = (end - start).days + 1
    class_num = 0
    for single_date in (start + datetime.timedelta(n) for n in range(day_count)):
        day_of_week = str(single_date.weekday())
        if day_of_week in days:
            if single_date in holidays:
                class_info['lec_num'] = "-"
                class_info['lec_date'] = single_date
                class_info['description'] = 'No class'
            else:
                if class_num < len(schedule):
                    class_info = schedule[class_num]
                else:
                    class_info = default_description
                class_num = class_num + 1
                class_info['lec_num'] = class_num
                class_info['lec_date'] = single_date
            print t.render(class_info)

    if args.footer is not None:
        with open(args.footer,'rt') as f:
            print f.read()


if __name__ == "__main__":
    main()
