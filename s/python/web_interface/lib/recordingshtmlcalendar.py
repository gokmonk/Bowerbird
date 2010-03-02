import datetime
from calendar import Calendar, SUNDAY, month_name, day_abbr

from lib.common import compactTimeFormat

class RecordingsHTMLCalendar(Calendar):

	def __init__(self, year, month, today, storage=None, filter=None,
			selected_date=None, selected_record=None, firstweekday=SUNDAY):
		self.year = year
		self.month = month
		self.today = today
		self.storage = storage
		self.filter = filter
		self.selected_date = selected_date
		self.selected_record = selected_record

		# initialise calendar source
		self.setfirstweekday(firstweekday)

	def showMonth(self):
		return self.formatMonth(self.year, self.month)

	def formatDay(self, themonth, date, num_weeks):
		"""
		Return a day as a table cell.
		"""
		if date.month != themonth:
			html = '<td class="noday' # day outside month
		else:
			html = '<td class="day'

		# if this is today then highlight it
		if date == self.today:
			html += ' today'
			today_text = 'Today '
		else:
			today_text = ''

		# if this is the selected date then tag it
		if (date == self.selected_date or (self.selected_record
				and date == self.selected_record.start_date)):
			html += ' selected'

		html += ('" style="height: %f%%"><div class="day_header">'
				'<a class="block" href="%s">%s%d</a></div>'
				% (90.0 / num_weeks, date.strftime('?year=%Y&month=%m&day=%d')
				+ '&clear_selected_recording=1', today_text, date.day))

		if self.storage:
			for recording in self.storage.getRecordings(date, self.filter):
				if (self.selected_record
						and recording.id == self.selected_record.id):
					extra_div_class = " selected_entry"
				else:
					extra_div_class = ""
				html += ('<div class="day_entry%s"><a class="block" '
						'href="?year=%d&month=%d&selected_record_id=%d">\n'
						'<span class="recording_time">%s</span>\n'
						'<span class="recording_title">%s</span>\n'
						'</a></div>\n' % (extra_div_class, date.year,
						date.month,	recording.id,
						compactTimeFormat(recording.start_time),
						recording.title))

		return html + '</td>'

	def formatWeek(self, themonth, theweek, num_weeks):
		"""
		Return a complete week as a table row.
		"""
		s = ''.join(self.formatDay(themonth, d, num_weeks) for d in theweek)
		return '<tr>%s</tr>' % s

	def formatWeekDay(self, day):
		"""
		Return a weekday name as a table header.
		"""
		return '<th class="day">%s</th>' % day_abbr[day]

	def formatWeekHeader(self):
		"""
		Return a header for a week as a table row.
		"""
		s = ''.join(self.formatWeekDay(i) for i in self.iterweekdays())
		return '<tr>%s</tr>' % s

	def formatMonthName(self, theyear, themonth, withyear=True,
			withlinks=True):
		"""
		Return a month name as a table row.
		"""
		if withyear:
			title = '%s %s' % (month_name[themonth], theyear)
		else:
			title = '%s' % month_name[themonth]

		if withlinks:
			prev_month = themonth - 1
			prev_month_year = theyear
			next_month = themonth + 1
			next_month_year = theyear
			if prev_month == 0:
				prev_month = 12
				prev_month_year -= 1
			elif next_month == 13:
				next_month = 1
				next_month_year += 1

			title = ('<a href="?year=%(py)d&month=%(m)d">'
					'&lt;&lt;</a>%(s)s'
					'<a href="?year=%(pmy)d&month=%(pm)d">'
					'&lt;</a>%(s)s'
					'%(title)s'
					'%(s)s<a href="?year=%(nmy)d&month=%(nm)d">'
					'&gt;</a>'
					'%(s)s<a href="?year=%(ny)d&month=%(m)d">'
					'&gt;&gt;</a>'
					% {'m': themonth, 'py': theyear-1,
						's': '&nbsp;&nbsp;', 'pm': prev_month,
						'pmy': prev_month_year, 'title': title,
						'nm': next_month, 'nmy': next_month_year,
						'ny': theyear+1	})

		return '<tr><th colspan="7" class="month">%s</th></tr>' % title


	def formatMonth(self, theyear, themonth, withyear=True):
		"""
		Return a formatted month as a table.
		"""
		html = ('<table class="month">\n%s\n%s\n'
				% (self.formatMonthName(theyear, themonth,
						withyear=withyear), self.formatWeekHeader()))
		weeks = self.monthdatescalendar(theyear, themonth)
		for week in weeks:
			html += self.formatWeek(themonth, week, len(weeks)) + '\n'
		return html + '</table>\n'
