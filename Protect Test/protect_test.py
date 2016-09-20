import sublime, sublime_plugin
from bs4 import BeautifulSoup
import sys

ID_REGIONS = []
TEST_FILE = None
TEST_SOUP = None
EDIT_FILE = None
LISTEN = True

def idSelectors(): #Retrieves all 'id' selectors from testfile. TEST_SOUP is a BeautifulSoup object
	testTableData = TEST_SOUP.find_all('td')
	idList = []
	for data in testTableData:
		if str(data.string).startswith('id',0,2):
			idList.append(data.string[3:]) #In a selector 'id=something, the something begins at position 3'
	return idList

def getRegions(view, selectorType, selectors): #Return an array of the regions to be highlighted
	regions = []
	for selector in selectors:
		searchString = selectorType + "=" + "\"" + selector + "\""
		print(searchString)
		selectorRegions = view.find_all(searchString) # add 'ignore case' flag
		for region in selectorRegions:
			critRegion = CriticalRegion(region, view)
			regions.append(critRegion)
	return regions

def getIDRegions(view):
	global ID_REGIONS
	idList = idSelectors()
	ID_REGIONS = getRegions(view, 'id', idList)
	highlightRegions(view, ID_REGIONS)

def highlightRegions(view, regions):
	regionList = []
	for region in regions:
		regionList.append(region.getRegion())
	view.add_regions('ThreatenedTestIDs', regionList, "invalid", "", 0)

def caretInRegion(region, caret_position):
	start = region.getRegion().a
	end = region.getRegion().b
	position = caret_position.a
	if position >= start and position <= end:
		return True
	else:
		return False

def caretBreachedCriticalRegion(caret_position, view): #If returns true, we have entered and exited a critical region
	global LISTEN
	for region in ID_REGIONS:
		if caretInRegion(region, caret_position):
			region.breach()
			LISTEN = False
		if not caretInRegion(region, caret_position) and region.beenBreached():
			if region.getText() != view.substr(region.getRegion()):
				print("CHANGE!!!")
				sublime.message_dialog("You just made a change that will potentially break your test file!")
			region.reset()
			return True
	return False

class CriticalRegion:
	def __init__(self, region, view):
		self.region = region
		self.text = view.substr(region)
		self.breached = False

	def breach(self):
		self.breached = True

	def reset(self):
		self.breached = False

	def beenBreached(self):
		return self.breached

	def getRegion(self):
		return self.region

	def getText(self):
		return self.text

class ProtectTestCommand(sublime_plugin.TextCommand): 
	def run(self, edit):
		global ID_REGIONS, TEST_FILE, TEST_SOUP, EDIT_FILE
		EDIT_FILE = str(self.view.file_name())
		try:
			htmlSoup = BeautifulSoup(open(EDIT_FILE), "lxml") #Open the html file
		except:
			print("There was an error opening the test file")
			return
		try:
			TEST_FILE = htmlSoup.meta['test'] #Look for html tag specifying location of test file, if applicable
		except KeyError:
			sublime.message_dialog("ERROR:No test file to open!")
			TEST_FILE = None
			return
		except TypeError:
			sublime.message_dialog("ERROR:No test file to open!")
			TEST_FILE = None
			return

		if TEST_FILE: #If we have a meta tag with a test attribute, look for the test file
			try: 
				TEST_SOUP = BeautifulSoup(open(TEST_FILE), "lxml")
				fileMapping = {'filePath': TEST_FILE}
				self.view.window().run_command("split_and_open", fileMapping)
			except:
				TEST_SOUP = False
				print("There was an error locating the test file!")
				e = sys.exc_info()[0]
				print(e)
				return
		if TEST_SOUP: #Get all id selectors
			getIDRegions(self.view)

class SplitAndOpenCommand(sublime_plugin.WindowCommand):
	def run(self, filePath):
		self.window.run_command("set_layout",{"cols": [0.0, 0.5, 1.0],"rows": [0.0, 1.0],"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
		self.window.focus_group(1)
		self.window.open_file(filePath)
		
class IDSelectorListener(sublime_plugin.EventListener):
	def on_selection_modified_async(self, view): #Triggered anytime the cursor moves or edit window is clicked
		if TEST_FILE and (EDIT_FILE == str(view.file_name())):
			if len(ID_REGIONS) > 0:
				print(ID_REGIONS)
				caret_position = view.sel()[0]
				if caretBreachedCriticalRegion(caret_position, view) == True:
					print("Trigger Event!!")
			else:
				pass

	def on_modified_async(self,view):#Each time the buffer changes due to added character
		if TEST_FILE and (EDIT_FILE == str(view.file_name())) and LISTEN:
			getIDRegions(view)
		else:
			pass