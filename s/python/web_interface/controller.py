import sys, os, os.path, shutil, errno, calendar, cherrypy
from subprocess import Popen, PIPE
from datetime import datetime
from lib import common, storage, ajax, template
from lib.sonogram import generateSonogram
from lib.configparser import ConfigParser
from genshi import HTML

# constants
RECORDING_KB_PER_SECOND = 700

# web interface config file
WEB_CONFIG = 'bowerbird.conf'
# parameters for parsing contents of web interface config file
CONFIG_KEY = 'bowerbird_config'
CONFIG_DEFAULTS_KEY = 'bowerbird_config_defaults'
DATABASE_KEY = 'database'
REQUIRED_KEYS = [CONFIG_KEY, DATABASE_KEY]
CONFIG_CACHE_PATH = 'config/current_config'

# general configuration
FREQUENCY_SCALES = ['Linear', 'Logarithmic']
DEFAULT_FFT_STEP = 256 # in milliseconds
SONOGRAM_DIRECTORY = os.path.join("static", "sonograms")

# parameters for parsing the contents of the bowerbird config file
STATION_SECTION_NAME = 'station_information'
STATION_NAME_KEY = 'name'
SCHEDULE_SECTION = 'scheduled_capture'

# paramaters for monitoring disk usage by sound capture
CAPTURE_SECTION_NAME = 'sound_capture'
CAPTURE_ROOT_DIR_KEY = 'sound_file_root_dir'


class Root(object):
	def __init__(self, db, path):
		self.db = db
		self.path = path

		config_filename = cherrypy.config[CONFIG_KEY]
		if not os.path.exists(config_filename):
			raise IOError(errno.ENOENT, "Config file '%s' not found" 
					% config_filename)

		if cherrypy.config.has_key(CONFIG_DEFAULTS_KEY):
			defaults_filename = cherrypy.config[CONFIG_DEFAULTS_KEY]
			# if defaults file doesn't exist, then don't use it
			if not os.path.exists(defaults_filename):
				sys.stderr.write("Warning: configured defaults file "
						" '%s' doesn't exist\n" % defaults_filename)
				defaults_filename = None
		else:
			defaults_filename = None

		self.conf = ConfigParser(config_filename, defaults_filename)


	@cherrypy.expose
	def index(self, **ignored):
		# just redirect to status page
		raise cherrypy.HTTPRedirect('/status')


	@cherrypy.expose
	@template.output('status.html')
	def status(self, **ignored):
		return template.render(station = self.get_station_name(),
				uptime = self.get_uptime(),
				disk_space = self.get_disk_space(),
				local_time = self.get_local_time(),
				last_recording = "?? Poison Dart Frogs (18:00-18:30)",
				next_recording = "?? Cane Toads (2:30-4:30)")


	@cherrypy.expose
	@template.output('config.html')
	def config(self, config_timestamp=0, load_defaults=False, cancel=False, 
			apply=False, export_config=False, new_config=None, 
			import_config=False, **data):
		error = None
		values = None

		if cancel:
			raise cherrypy.HTTPRedirect('/')
		elif export_config:
			# use cherrypy utility to push the file for download. This also means
			# that we don't have to move the config file into the web-accessible
			# filesystem hierarchy
			return cherrypy.lib.static.serve_file(
					os.path.realpath(self.conf.filename), 
					"application/x-download", "attachment",
					os.path.basename(self.conf.filename))
		elif apply:
			# if someone else has modified the config, then warn the user
			# before saving their changes (overwriting the other's changes)
			if int(config_timestamp) == self.conf.get_timestamp():
				self.updateConfigFromPostData(self.conf, data)

				# update file
				try:
					self.conf.save_to_file()
					self.conf.export_for_shell(self.conf.filename + ".sh")
					# bounce back to homepage
					raise cherrypy.HTTPRedirect('/')
				except IOError as e:
					# if save failed, put up error message and stay on the page
					error = 'Error saving: %s' % e
			else:
				error = HTML('''WARNING:
						Configuration has been changed externally.<br />
						If you wish to keep your changes and lose the external
						changes, then click on 'Apply' again. <br />
						To lose your changes and preserve the external changes, 
						click 'Cancel'.''')
				# load the post data into a temporary configparser to preserve
				# the user's changes when the page is loaded again. This means
				# we don't have to duplicate the horrible POST-to-config code
				temp_conf = ConfigParser()
				self.updateConfigFromPostData(temp_conf, data)
				values = temp_conf.get_values()
				# the page loading below will send the new config timestamp so
				# we don't have to anything else here.

		if load_defaults:
			values = self.conf.get_default_values()
		elif import_config:
			if new_config.filename:
				try:
					values = self.conf.parse_file(new_config.file)
				except Exception as e:
					values = None
					error = 'Unable to parse config file: "%s"' % e
			else:
				error = 'No filename provided for config import'

		if not values:
			values = self.conf.get_values()
		return template.render(station=self.get_station_name(), 
				config_timestamp=self.conf.get_timestamp(),
				error=error, using_defaults=load_defaults, values=values,
				file=self.conf.filename, 
				defaults_file=self.conf.defaults_filename)


	@cherrypy.expose
	@template.output('schedule.html')
	def schedule(self, load_defaults=None, cancel=None, apply=None, add=None,
			**data):
		error = None
		if cancel:
			raise cherrypy.HTTPRedirect('/')
		elif apply:
			# clear all schedules and add them back in the order they were on the webpage
			self.conf.clear_schedules()
			schedules = {}

			# just get the labels
			for key in data:
				# each schedule comes in three parts: ?.label, ?.start, ?.finish
				if key.endswith('label'):
					id = key.split('.')[0]
					schedules[id] = data[key]

			# sort the labels by their id, then add them in that order
			schedule_ids = schedules.keys()
			schedule_ids.sort()
			for id in schedule_ids:
				start_key = "%s.start" % id
				finish_key = "%s.finish" % id
				if data.has_key(start_key) and data.has_key(finish_key):
					schedule_key = schedules[id]
					schedule_value = "%s - %s" \
							% (data[start_key], data[finish_key])
					self.conf.set_schedule(schedule_key, schedule_value)

			# update file
			try:
				self.conf.save_to_file()
				self.conf.export_for_shell(self.conf.filename + ".sh")
				# bounce back to homepage
				raise cherrypy.HTTPRedirect('/')
			except IOError as e:
				# if save failed, put up error message and stay on the page
				error = "Error saving: %s" % e

		elif not add:
			# this should only happen when a remove button has been clicked
			# find the remove key
			for key in data:
				if key.endswith('remove'):
					# get the schedule key from the label
					id = key.split('.')[0]
					label_key = "%s.label" % id
					if data.has_key(label_key):
						schedule_key = data[label_key]
						self.conf.delete_schedule(schedule_key)

		if load_defaults:
			values = self.conf.get_default_schedules()
		else:
			values = self.conf.get_schedules()

		return template.render(station=self.get_station_name(), error=error,
				using_defaults=load_defaults, values=values, add=add,
				section=SCHEDULE_SECTION, file=self.conf.filename, 
				defaults_file=self.conf.defaults_filename)

	@cherrypy.expose
	@template.output('recordings.html')
	def recordings(self, **ignored):
		recording_calendar = calendar.HTMLCalendar(calendar.SUNDAY)
		recordings = ["Cane Toads (2:30-4:30)", 
				"Poison Dart Frogs (18:00-18:30)"]
		return template.render(station=self.get_station_name(),
				recordings=recordings,
				calendar=HTML(recording_calendar.formatmonth(2010,2,True)))

	
#	@cherrypy.expose
	@template.output('categories.html')
	def categories(self, sort='label', sort_order='asc', **ignored):
		categories_var = self.db.getCategories(sort, sort_order)
		return template.render(station=self.get_station_name(),
				categories=categories_var,
				sort=sort, sort_order=sort_order)


#	@cherrypy.expose
	@template.output('category.html')
	def category(self, label=None, new_label=None, update_details=None,
			sort='date_and_time', sort_order='asc', **ignored):
		if update_details and new_label and new_label != label:
			self.db.updateCategory(label, new_label)
			raise cherrypy.HTTPRedirect('/category/%s' % new_label)

		calls = self.db.getCalls(sort, sort_order, label)
		call_sonograms = {}
		for call in calls:
			call_sonograms[call['filename']] = self.getSonogram(call, FREQUENCY_SCALES[0], DEFAULT_FFT_STEP)
		return template.render(station=self.get_station_name(), \
				category=self.db.getCategory(label),
				calls=calls, call_sonograms=call_sonograms, sort=sort, sort_order=sort_order)


#	@cherrypy.expose
	@template.output('calls.html')
	def calls(self, sort='date_and_time', sort_order='asc', category=None, **ignored):
		return template.render(station=self.get_station_name(), \
				calls=self.db.getCalls(sort, sort_order, category),
				sort=sort, sort_order=sort_order)


#	@cherrypy.expose
	@template.output('call.html')
	def call(self, call_filename=None,
			update_details=None, label=None, category=None, example=None,
			update_sonogram=None, frequency_scale=FREQUENCY_SCALES[0],
			fft_step=DEFAULT_FFT_STEP,
			**ignored):
		if not call_filename:
			raise cherrypy.NotFound()

		fft_step = int(fft_step)

		if call_filename and update_details:
			self.db.updateCall(call_filename, label, category, example)
			if ajax.is_xhr():
				return # ajax update doesn't require a response

		call=self.db.getCall(call_filename)
		if ajax.is_xhr():
			# only sonogram updates are possible here
			assert(update_sonogram)
			return template.render('_sonogram.html', ajah=True,
					sonogram_filename=self.getSonogram(call, frequency_scale, fft_step),
					fft_step=fft_step, frequency_scale=frequency_scale,
					frequency_scales=FREQUENCY_SCALES)
		else:
			return template.render(station=self.get_station_name(), call=call,
					categories=",".join(self.db.getCategoryNames()),
					sonogram_filename=self.getSonogram(call, frequency_scale, fft_step),
					fft_step=fft_step, frequency_scale=frequency_scale,
					frequency_scales=FREQUENCY_SCALES,
					prev_next_files=self.db.getPrevAndNextCalls(call))


	def get_station_name(self):
		return self.conf.get_value2(STATION_SECTION_NAME, STATION_NAME_KEY)


	def updateConfigFromPostData(self, config, data):
		# clear out the configuration and re-populate it
		config.clear_config()

		# parse the data, then sort it so it can be entered in the same order we
		# sent it (to preserve the order that gets mixed up by the POST data)
		sections = {}
		keys = {}
		values = {}
		for key in data:
			if key.startswith(common.META_PREFIX):
				split_data = data[key].split(',')
				section_index = int(split_data[0])
				name_index = int(split_data[1])
				subname_index = int(split_data[2])
				value = ','.join(split_data[3:])
				real_key = key[len(common.META_PREFIX):]
				if not keys.has_key(section_index):
					keys[section_index] = {}
				if not keys[section_index].has_key(name_index):
					keys[section_index][name_index] = {}
				keys[section_index][name_index][subname_index] \
						= (real_key, value)
			elif key.startswith(common.SECTION_META_PREFIX):
				index = data[key].find(',')
				id = int(data[key][:index])
				value = data[key][index+1:]
				real_key = key[len(common.SECTION_META_PREFIX):]
				sections[id] = (real_key, value)
			else:
				values[key] = data[key]

		# first insert the sections in sorted order
		section_indicies = sections.keys()
		section_indicies.sort()
		for section_index in section_indicies:
			key, value = sections[section_index]
			config.set_smeta(key, value)

		# next insert the key meta data in sorted order
		section_indicies = keys.keys()
		section_indicies.sort()
		for section_index in section_indicies:
			name_indicies = keys[section_index].keys()
			name_indicies.sort()
			for name_index in name_indicies:
				subname_indicies = keys[section_index][name_index].keys()
				subname_indicies.sort()
				for subname_index in subname_indicies:
					key, value = keys[section_index][name_index][subname_index]
					config.set_meta1(key, value)

		# now set the actual values
		for key in values:
			config.set_value1(key, values[key])


	def getSonogram(self, call, frequency_scale, fft_step):
		if call:
			destination_dir = os.path.abspath(SONOGRAM_DIRECTORY)
			return '/media/sonograms/%s' % generateSonogram(call['filename'], 
					destination_dir, frequency_scale, fft_step)
		return ''


	def get_uptime(self):
		return Popen("uptime", stdout=PIPE).communicate()[0]


	def get_disk_space(self):
		root_dir = self.conf.get_value2(CAPTURE_SECTION_NAME,
				CAPTURE_ROOT_DIR_KEY)
		if not os.path.exists(root_dir):
			return "%s doesn't exist: Fix Config %s->%s" \
					% (root_dir, CAPTURE_SECTION_NAME, CAPTURE_ROOT_DIR_KEY)
		# split to remove title line, then split into fields
		(_,_,_,available,percent,_) = Popen(["df", "-k", root_dir],
				stdout=PIPE).communicate()[0].split('\n')[1].split()
		percent_free = 100 - int(percent[:-1])
		available = int(available)
		return "%s free (%d%%) Approx. %s recording time left" \
				% (pretty_size(available), percent_free, 
						pretty_time(available/RECORDING_KB_PER_SECOND))


	def get_local_time(self):
		now = datetime.now()
		# TODO add info about sunrise/set relative time
		# "18:36 (1 hour until sunset), 1st February 2010"
		return now.strftime("%H:%M, %d %B %Y")


def pretty_size(kilobytes):
	sizes = [ (1024**3, "T"), (1024**2, "G"), (1024, "M"), (1, "k") ]
	for size,unit in sizes:
		if kilobytes > size:
			return "%.1f%sB" % (float(kilobytes) / size, unit)
	return "error generating pretty size for %f" % kilobytes


def pretty_time(seconds, show_seconds=False):
	sizes = [ (365*24*60*60, "years"), (30*24*60*60, "months"), 
			(24*60*60, "days"), (60*60, "hours"), 
			(60, "minutes"), (1, "seconds") ]
	if not show_seconds:
		sizes = sizes[:-1]
	pretty = ""
	for size,unit in sizes:
		if seconds > size:
			pretty += "%d %s " % (seconds / size, unit)
			seconds %= size
	return pretty


def loadWebConfig():
	# load config from file
	cherrypy.config.update(WEB_CONFIG)

	# set static directories to be relative to script
	cherrypy.config.update({
			'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
			})

	for key in REQUIRED_KEYS:
		if not cherrypy.config.has_key(key):
			sys.stderr.write('Web config file "%s" is missing definition for "%s"\n'
					% (WEB_CONFIG, key))
			return False

	return True


def main(args):
	# check minimum settings are specified in config
	if not loadWebConfig():
		sys.exit(1)

	# initialise storage
	database_file = cherrypy.config[DATABASE_KEY]
	if not os.path.exists(database_file):
		sys.stderr.write('Warning: configured database file '
				'"%s" does not exist. Creating a new one...\n'
				% database_file)
	db = storage.Storage(database_file)
	# make sure that database has key tables
	if not db.hasRequiredTables():
		sys.stderr.write('Warning: configured database file '
				'"%s" missing required tables. Creating them...\n'
				% database_file)
		db.createRequiredTables()

	cherrypy.engine.subscribe('stop_thread', db.stop)

	path = os.path.dirname(os.path.realpath(args[0]))

	try:
		cherrypy.tree.mount(Root(db, path), '/', {
			'/media': {
				'tools.staticdir.on': True,
				'tools.staticdir.dir': 'static'
			}
		})
	except IOError as e:
		sys.stderr.write('Error: %s.\n' % e);
		sys.exit(1)

	cherrypy.engine.start()
	cherrypy.engine.block()


if __name__ == '__main__':
	main(sys.argv)
