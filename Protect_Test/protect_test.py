import sublime, sublime_plugin
from bs4 import BeautifulSoup
from .lib import globals, test_utils, parse_utils, region_utils, info_utilities

import sys

class ProtectTestCommand(sublime_plugin.TextCommand): 
	def run(self, edit):

		#Try to open file under test
		globals.EDIT_FILE = str(self.view.file_name())
		try:
			htmlSoup = BeautifulSoup(open(globals.EDIT_FILE), "lxml") #Open the html file
		except:
			print("There was an error opening the test file")
			e = sys.exc_info()[0]
			print(e)
			return

		#Look for a meta tag identifying a test file
		try:
			globals.TEST_FILE = htmlSoup.meta['test'] #Look for html tag specifying location of test file, if applicable
		except:
			sublime.message_dialog("ERROR:No test file to open. Include a meta tag, with a 'test' attribute pointing to the file path of the test file")
			globals.TEST_FILE = None
			return
	

		if globals.TEST_FILE: #If we have a meta tag with a test attribute, try to open the test file
			try: 
				globals.TEST_SOUP = BeautifulSoup(open(globals.TEST_FILE), "lxml")
				fileMapping = {'filePath': globals.TEST_FILE}
				# self.view.window().run_command("split_and_open", fileMapping) #Was used to split the window
			except:
				globals.TEST_SOUP = False
				print("There was an error locating the test file!")
				e = sys.exc_info()[0]
				print(e)
				return

		#Finally, if there is a test file, parse it and build the test data		
		if globals.TEST_SOUP: 
			globals.TEST_LIST = test_utils.buildTestData()
			print(globals.TEST_LIST)
			test_utils.processTestsInitial(globals.TEST_LIST, self.view)
			for region in globals.REGION_LIST:
				print(region.text)
				print(region.test)
			

class SplitAndOpenCommand(sublime_plugin.WindowCommand):#This just creates a split-pane view with test/under_test
	def run(self, filePath):
		self.window.run_command("set_layout",{"cols": [0.0, 0.5, 1.0],"rows": [0.0, 1.0],"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
		self.window.focus_group(1)
		self.window.open_file(filePath)
		
class EditListener(sublime_plugin.EventListener):
	def on_selection_modified_async(self, view): #Triggered anytime the cursor moves or edit window is clicked
		if globals.TEST_FILE and (globals.EDIT_FILE == str(view.file_name())):
			#info_utilities.printStatusOfEverything(view)
			tree = parse_utils.getViewTree(view)
			test_utils.processTests(globals.TEST_LIST, tree)
			
	def on_modified_async(self,view):#Each time the buffer changes due to added character
		region_utils.updateRegions(view)

class HoverListener(sublime_plugin.ViewEventListener):
	def on_hover(self,point, hover_zone):
		if hover_zone == sublime.HOVER_TEXT:
			region_utils.pointInCriticalRegion(point, self.view)
