import sublime, sublime_plugin
from bs4 import BeautifulSoup
from .lib import globals, test_utils, parse_utils, region_utils, info_utilities
from .models.protected_test import ProtectedTest

import sys

def plugin_loaded():
	for protected_test in sublime.load_settings('protect_test.sublime-settings').get('protected_tests'):
		if not test_utils.filePresent(protected_test):
			sublime.error_message("PROTECT TEST: " + protected_test + " cannot be found!")
			continue
		test = ProtectedTest(protected_test)
		globals.PROTECTED_TESTS.append(test)
	print(globals.PROTECTED_TESTS)
	if globals.PROTECTED_TESTS: #Wrap with try/except?
		test_utils.buildTestData()
	info_utilities.printProtectedTestInfo()
	test_utils.verifyTestsInitial()
	# for protected_test in globals.PROTECTED_TESTS:
	# 	for file in protected_test.filesUnderTest:
	# 		test_utils.processTestsInitial(file)
	#print(individualTests)

# class ProtectTestCommand(sublime_plugin.TextCommand): 
# 	def run(self, edit):

# 		#Try to open file under test
# 		globals.EDIT_FILE = str(self.view.file_name())

# 		#Look for a meta tag identifying a test file
# 		try:
# 			globals.TEST_FILES = parse_utils.getTestFiles() #Look for html tag specifying location of test file, if applicable
# 		except:
# 			sublime.message_dialog("ERROR:No test file to open. Include a meta tag, with a 'test' attribute pointing to the file path of the test file")
# 			globals.TEST_FILES = None
# 			e = sys.exc_info()[0]
# 			print(e)
# 			return
	
# 		print(globals.TEST_FILES)
# 		#Finally, if there is a test file, parse it and build the test data		
# 		if globals.TEST_FILES: 
# 			globals.TEST_LIST = test_utils.buildTestData()
# 			print(globals.TEST_LIST)
# 			test_utils.processTestsInitial(globals.TEST_LIST, self.view)
# 			globals.LISTEN = True
# 			for region in globals.REGION_LIST:
# 				print(region.text)
# 				print(region.test)
			

# class SplitAndOpenCommand(sublime_plugin.WindowCommand):#This just creates a split-pane view with test/under_test
# 	def run(self, filePath):
# 		self.window.run_command("set_layout",{"cols": [0.0, 0.5, 1.0],"rows": [0.0, 1.0],"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
# 		self.window.focus_group(1)
# 		self.window.open_file(filePath)
		
class EditListener(sublime_plugin.EventListener):
	def on_selection_modified_async(self, view): #Triggered anytime the cursor moves or edit window is clicked
		if globals.LISTEN and (globals.ACTIVE_FILE.path == str(view.file_name())):
			print("edit listener triggered")
			tree = parse_utils.getViewTree(view)
			test_utils.processTests(globals.ACTIVE_FILE.tests, tree, view, globals.ACTIVE_FILE)
			print(globals.ACTIVE_FILE.tests)
			for test in globals.ACTIVE_FILE.tests:
				if test.region is not None:
					if test.fold:
						view.fold(test.region)
					else:
						view.unfold(test.region)
			
# 	# def on_modified_async(self,view):#Each time the buffer changes due to added character
# 	# 	if globals.LISTEN and (globals.EDIT_FILE == str(view.file_name())):
# 	# 		region_utils.updateRegions(view)

class ViewListener(sublime_plugin.ViewEventListener):
	def on_hover(self, point, hover_zone):
		if globals.ACTIVE_FILE is not None:
			print("HOVERIN -- " + str(globals.ACTIVE_FILE.path) + " --- " + self.view.file_name())
			if globals.ACTIVE_FILE.path == self.view.file_name() and hover_zone == sublime.HOVER_TEXT:
				print("Hover Listen Trigger")
				region_utils.pointInCriticalRegion(point, self.view)

	def on_activated_async(self):
		globals.LISTEN = False
		#Set globals.ACTIVE_FILE = None?
		for protected_test in globals.PROTECTED_TESTS:
			for file in protected_test.filesUnderTest:
				if file.path == self.view.file_name():
					print("This file is protected!")
					globals.ACTIVE_FILE = file
					globals.LISTEN = True
		if globals.ACTIVE_FILE is not None:
			print(globals.ACTIVE_FILE.path)
			print("Listening: " + str(globals.LISTEN))
