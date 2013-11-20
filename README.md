MAKE-SYLLABUS
=============
Micah Sherr, 2013
Georgetown University
msherr@cs.georgetown.edu



### Installation

Do the following:

* mkdir -p ~/env/makesyllabus
* virtualenv ~/env/makesyllabus
* source ~/env/makesyllabus/bin/activate
* pip install python-dateutil
* pip install pyaml
* pip install jinja2
* pip install icalendar



### Usage

To use make-syllabus, make sure that you have the correct python environment set up.  First, do:

    % source ~/env/makesyllabus/bin/activate

Then, for usage instructions, do

    % python make-syllabus.py -h


### Examples

* python make-syllabus.py --start "january 8, 2014" --end "april 28, 2014" --days 02 --schedule schedules/cosc755-spring2014.yaml --ical cosc755-spring2014.ics --starttime 3:30pm --endtime 4:45pm --holidays "1/20/2014:2/17/2014:3/8/2014#3/16/2014:4/17/2014#4/21:2014" --course COSC755

