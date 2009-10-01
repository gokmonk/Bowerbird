#!/usr/bin/env python

# parse the config file to find times to record and then generate a crontab
# file that will cause those recordings to happen

# TODO error checking

import sys, re, time
from datetime import datetime, timedelta
from math import floor
from sun import Sun
from bowerbird.configobj import ConfigObj

# location of configuration file
DEFAULT_USER = 'root' # the user to execute the command to put in crontab
DEFAULT_DAYS_TO_SCHEDULE = 7
DEFAULT_CONFIG_FILENAME = '../bowerbird_config'

STATION_SECTION = 'station_information'
STATION_TZ_KEY = 'tz_offset'
STATION_LAT_KEY = 'latitude'
STATION_LONG_KEY = 'longitude'

CONFIG_SECTION = 'sound_capture'
CONFIG_COMMAND = 'schedule_command'
CONFIG_USER = 'schedule_user'
CONFIG_DAYS_KEY = 'schedule_days'

SCHEDULE_SECTION = 'scheduled_recordings'
TIMESPEC_RE = re.compile('([SR]?)([+-]?[0-9]{1,2}):([0-9]{2}) *- '
						'*([SR]?)([+-]?[0-9]{1,2}):([0-9]{2})')

# check value is a valid array of recording times
def parseRecordingSpec(key, value):
	# check for single elements
	if type(value) == str:
		value = [value]
	specs = []
	# parse each time specification
	for spec in value:
		match = TIMESPEC_RE.match(spec)
		if match:
			start_type, start_hour, start_minute, end_type, end_hour, end_minute \
				= match.groups()
			specs.append(((start_type, 
					timedelta(hours=int(start_hour), minutes=int(start_minute))),
					(end_type,
					timedelta(hours=int(end_hour), minutes=int(end_minute)))))
		else:
			sys.stderr.write('%s has invalid recording spec: %s->%s: %s\n'
					% (config_filename, SCHEDULE_SECTION, key, spec))
			sys.exit(1)
	return specs

# TODO search for this file in a number of places
# TODO accept config path on the commandline
config_filename = DEFAULT_CONFIG_FILENAME
command = None
user = None
days_to_schedule = None
tz_offset = None
latitude = None
longitude = None

# read configuration file
config = ConfigObj(config_filename)
# read station information
section = config[STATION_SECTION]
for key in section:
	if key == STATION_TZ_KEY:
		# get timezone from config
		tz_offset = int(section[key])
	elif key == STATION_LAT_KEY:
		# get latitude from config
		latitude = float(section[key])
	elif key == STATION_LONG_KEY:
		# get longitude from config
		longitude = float(section[key])

# read sound capture info
section = config[CONFIG_SECTION]
for key in section:
	if key == CONFIG_COMMAND:
		command = section[key]
	elif key == CONFIG_USER:
		user = section[key]
	elif key == CONFIG_DAYS_KEY:
		days_to_schedule = int(section[key])

# check config had enough info, and fill in defaults if available
if not command:
	sys.stderr.write('%s must be specified in the %s section of "%s"\n'
			% (CONFIG_COMMAND, CONFIG_SECTION, config_filename));
if not user:
	user = DEFAULT_USER
if not days_to_schedule:
	days_to_schedule = DEFAULT_DAYS_TO_SCHEDULE
# if timezone is not specified in config, then get it from python
if not tz_offset:
	# python tz offsets are negative and in seconds
	tz_offset = -time.timezone / 3600
if not latitude or not longitude:
	# eventually ask GPS
	sys.stderr.write('%s and %s must be specified in the %s section of "%s"'
				'(at least until we can talk to the GPS)\n'
			% (CONFIG_LAT_KEY, CONFIG_LONG_KEY, CONFIG_SECTION, config_filename));


# parse the requested recording times
recording_times = []
section = config[SCHEDULE_SECTION]
for key in section:
	recording_times.extend(parseRecordingSpec(key, section[key]))

# get current day
today = datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
# get a sun calculating object
sun = Sun()

# print preamble
print '''# system crontab automatically generated by %s
# to schedule daily sound capturing.

# Do not edit directly as it will be overwritten

# use /bin/bash to run commands, instead of the default /bin/sh
SHELL=/bin/bash
# set path so we can find all commands
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m\th\tdom\tmon\tdow\tuser\tcommand''' % sys.argv[0]

converted_recording_times = []
for i in range(days_to_schedule):
	# TODO iterate from current day to days_to_schedule
	day = today + timedelta(days=i)
	#TODO optimisation: skip sunrise/set calc if all times are absolute
	rise, set = [timedelta(hours=(t + tz_offset)) for t in 
			sun.sunRiseSet(day.year, day.month, day.day, longitude, latitude)]
	for ts in recording_times:
		recording_time = []
		for t in ts:
			if t[0] == 'R':
				rt = day + rise + t[1]
			elif t[0] == 'S':
				rt = day + set + t[1]
			else:
				rt = day + t[1]
			recording_time.append(rt)
		converted_recording_times.append(recording_time)

# sort times to make algorithm easy
converted_recording_times.sort()
cron_times = []
start = None
finish = None
for recording_time in converted_recording_times:
	if start == None:
		# new duration starting
		start, finish = recording_time
	else:
		if recording_time[0] < finish:
			# if current overlaps previous times
			if recording_time[1] > finish:
				# if it extends previous times
				finish = recording_time[1]
		else:
			# no overlap so save current duration
			cron_times.append((start, finish))
			# initialise next duration
			start, finish = recording_time
# save the last duration
if start != None:
	cron_times.append((start, finish))

for start,finish in cron_times:
	command_str = command % (finish - start).seconds
	print '%d\t%d\t%d\t%d\t*\t%s\t%s' % (start.minute, start.hour, 
			start.day, start.month, user, command_str)