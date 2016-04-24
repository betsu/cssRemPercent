import sublime
import sublime_plugin
import re
import time
import os

SETTINGS = {}
lastCompletion = {"needFix": False, "valueRem": None, "valuePercent":None, "region": None}

def plugin_loaded():
	init_settings()

def init_settings():
	get_settings()
	sublime.load_settings('cssrem.sublime-settings').add_on_change('get_settings', get_settings)

def get_settings():
	settings = sublime.load_settings('cssrem.sublime-settings')
	SETTINGS['px_to_rem'] = settings.get('px_to_rem', 320)
	SETTINGS['px_to_percent'] = settings.get('px_to_percent', 320)
	SETTINGS['max_rem_fraction_length'] = settings.get('max_rem_fraction_length', 6)
	SETTINGS['max_percent_fraction_length'] = settings.get('max_percent_fraction_length', 3)
	SETTINGS['available_file_types'] = settings.get('available_file_types', ['.css', '.less', '.sass'])

def get_setting(view, key):
	return view.settings().get(key, SETTINGS[key]);

class RootRemCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.show_input_panel("rem root(px):", "", self.on_done, None, None)
		pass
	def on_done(self, text):
		try:
			width = int(text)
			if self.window.active_view():
				self.window.active_view().run_command("root_rem_set", {"content":width})
		except ValueError:
			pass

class RootRemSetCommand(sublime_plugin.TextCommand):
	def run(self, edit, content):
		width = int(content)
		SETTINGS['px_to_rem'] = width

class RootWidthCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.show_input_panel("計算 margin padding %值的區塊寬度(px):", "", self.on_done, None, None)
		pass
	def on_done(self, text):
		try:
			width = int(text)
			if self.window.active_view():
				self.window.active_view().run_command("root_width_set", {"content":width})
		except ValueError:
			pass

class RootWidthSetCommand(sublime_plugin.TextCommand):
	def run(self, edit, content):
		width = int(content)
		SETTINGS['px_to_percent'] = width

class CssUnitCommand(sublime_plugin.EventListener):
	def on_text_command(self, view, name, args):
		if name == 'commit_completion':
			view.run_command('replace_unit')
		return None

	def on_query_completions(self, view, prefix, locations):
		# print('cssrem start {0}, {1}'.format(prefix, locations))


		# only works on specific file types
		fileName, fileExtension = os.path.splitext(view.file_name())
		if not fileExtension.lower() in get_setting(view, 'available_file_types'):
			return []

		# reset completion match
		lastCompletion["needFix"] = False
		location = locations[0]
		snippets = []

		# get rem match
		match = re.compile("([\d.]+)p(x)?").match(prefix)
		if match:
			lineLocation = view.line(location)
			line = view.substr(sublime.Region(lineLocation.a, location))
			value = match.group(1)
			
			# fix: values like `0.5px`
			segmentStart = line.rfind(" ", 0, location)
			if segmentStart == -1:
				segmentStart = 0
			segmentStr = line[segmentStart:location]

			segment = re.compile("([\d.])+" + value).search(segmentStr)
			if segment:
				value = segment.group(0)
				start = lineLocation.a + segmentStart + 0 + segment.start(0)
				lastCompletion["needFix"] = True
			else:
				start = location

			remValue = round(float(value) / get_setting(view, 'px_to_rem'), get_setting(view, 'max_rem_fraction_length'))
			percentValue = round(float(value) / get_setting(view, 'px_to_percent') * 100, get_setting(view, 'max_percent_fraction_length'))

			# save them for replace fix
			lastCompletion["valueRem"] = str(remValue) + 'rem' 
			lastCompletion["valuePercent"] = str(percentValue) + '%' 
			lastCompletion["region"] = sublime.Region(start, location)

			# set completion snippet
			snippets += [(value + 'px ->rem(' + str(get_setting(view, 'px_to_rem')) + ')', str(remValue) + 'rem')]
			snippets += [(value + 'px ->%(' + str(get_setting(view, 'px_to_percent')) + ')', str(percentValue) + '%')]

		# print("cssrem: {0}".format(snippets))
		return snippets

class ReplaceUnitCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		needFix = lastCompletion["needFix"]
		if needFix == True:
			valueRem = lastCompletion["valueRem"]
			valuePercent = lastCompletion["valuePercent"]
			region = lastCompletion["region"]
			# print('replace: {0}, {1}'.format(value, region))
			self.view.replace(edit, region, value)
			self.view.end_edit(edit)