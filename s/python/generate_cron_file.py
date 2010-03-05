#!/usr/bin/env python

# parse the config file to find times to record and then generate a crontab
# file that will cause those recordings to happen

# TODO error checking

# TODO add invoking of assemble_recording_files.py

import sys
from bowerbird.scheduleparser import ScheduleParser

# location of configuration file
DEFAULT_USER = 'root' # the user to execute the command to put in crontab
DEFAULT_DAYS_TO_SCHEDULE = 7
DEFAULT_CONFIG_FILENAME = '../bowerbird_config'
DEFAULT_SCHEDULE_FILENAME = '../bowerbird_schedule'

# TODO search for this file in a number of places
# TODO accept config path on the commandline
config_filename = DEFAULT_CONFIG_FILENAME
schedule_filename = DEFAULT_SCHEDULE_FILENAME

# read configuration file
schedule = ScheduleParser(config_filename, schedule_filename)

# check config had enough info, and fill in defaults if available
if not schedule.assertCommandIsDefined():
	sys.exit(1)

if not schedule.user:
	schedule.user = DEFAULT_USER
if not schedule.days_to_schedule:
	schedule.days_to_schedule = DEFAULT_DAYS_TO_SCHEDULE


# print preamble
print '''# system crontab automatically generated by
# %s
# to schedule daily sound capturing.

# Do not edit directly as it will be overwritten

# use /bin/bash to run commands, instead of the default /bin/sh
SHELL=/bin/bash
# set path so we can find all commands
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m\th\tdom\tmon\tdow\tuser\tcommand''' % sys.argv[0]

cron_times = []
start = None
finish = None
for recording_time in schedule.getRecordingTimes():
	if start == None:
		# new duration starting
		start, finish = recording_time.getStartAndFinish()
	else:
		if recording_time.start < finish:
			# if current overlaps previous times
			if recording_time.finish > finish:
				# if it extends previous times
				finish = recording_time.finish
		else:
			# no overlap so save current duration
			cron_times.append((start, finish))
			# initialise next duration
			start, finish = recording_time.getStartAndFinish()
# save the last duration
if start != None:
	cron_times.append((start, finish))

for start,finish in cron_times:
	command_str = schedule.command % (finish - start).seconds
	print '%d\t%d\t%d\t%d\t*\t%s\t%s' % (start.minute, start.hour,
			start.day, start.month, schedule.user, command_str)
