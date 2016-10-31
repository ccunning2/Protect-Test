import sublime, sublime_plugin
from bs4 import BeautifulSoup
from lxml import etree as ET
import sys

ID_REGIONS = []
NODE_REGIONS = []
TEST_FILE = None
TEST_SOUP = None
EDIT_FILE = None
LISTEN = True

def printRegionInfo(): #To print critical region information for debugging
	for crit_region in NODE_REGIONS:
		print("Region locator: " + str(crit_region.getTest().getLocator()) + " Region:" + str(crit_region.region.a) + " thru " + str(crit_region.region.b))
	print('--------------\n')

def printStatusOfEverything(view):
	print("Listen is: " + str(LISTEN) + "\n")
	print("Cursor is at: " + str(view.sel()[0].a) + "\n")
	printRegionInfo()

def getTree(view): #Returns parse tree via lxmlimport(For use with XPath tasks)
	return ET.fromstring(view.substr(sublime.Region(0, view.size())))

def idSelectors(): #Retrieves all 'id' selectors from testfile. TEST_SOUP is a BeautifulSoup object
	testTableData = TEST_SOUP.find_all('td')
	idList = []
	for data in testTableData:
		if str(data.string).startswith('id',0,2):
			idList.append(data.string[3:]) #In a selector 'id=something, the something begins at position 3'
	return idList

def buildTestData(): #Retrieves all test data from testfile
	rows = TEST_SOUP.find_all('tr')
	testList = []
	#Get rid of first two rows
	rows.pop(0)
	rows.pop(0)
	for row in rows:
		tempData = row.find_all('td')
		testData = SeleniumTestData(tempData[0].text)
		testData.setLocator(tempData[1].text)
		testData.setText(tempData[2].text)
		testList.append(testData)
	return testList


def getRegionByLines(line1, line2, view): #Returns the legion starting at the beginning of line1 and the end of line 2 
	a = view.text_point(line1-1, 0)
	lastCol = view.line(view.text_point(line2-1, 0)).b
	return sublime.Region(a, lastCol)

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

def getXpathRegions(view, testList):
	global NODE_REGIONS
	NODE_REGIONS = [] #Clear Node Regions
	#Construct lxml etree
	etree = getTree(view)
	for test in testList:
		#get element
		element = etree.xpath(test.getLocator())[0]
		beginLine = element.sourceline
		endLine = element.getnext().sourceline - 1
		region = getRegionByLines(beginLine,  endLine, view)
		NODE_REGIONS.append(CriticalRegion(region,test,view))


def getNodeRegions(view):
	testList = buildTestData()
	print(testList)
	getXpathRegions(view, testList)
	highlightRegions(view, NODE_REGIONS)

def getIDRegions(view):
	global ID_REGIONS
	idList = idSelectors()
	ID_REGIONS = getRegions(view, 'id', idList)
	highlightRegions(view, ID_REGIONS)

def highlightRegions(view, regions):
	print("Highlighting Regions\n")
	regionList = []
	for region in regions:
		regionList.append(region.getRegion())
	view.add_regions('CritRegions', regionList, "invalid", "", 0)

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
	for region in NODE_REGIONS:
		if caretInRegion(region, caret_position):
			print("Region Breach!\n")
			region.breach()
			LISTEN = False
		if not caretInRegion(region, caret_position) and region.beenBreached():
			if region.getText() != view.substr(region.getRegion()):
				print("CHANGE!!!")
				sublime.message_dialog("You just made a change that will potentially break your test file!")
			region.reset() #Modify this to reset region text?
			LISTEN = True #Resume listening
			return True
	return False

class SeleniumTestData:
	def __init__(self, test):
		self.test = test
		self.locator = ""
		self.text = ""

	def getTest(self):
		return self.test

	def getLocator(self):
		return self.locator

	def getText(self):
		return self.text

	def setLocator(self, locator):
		self.locator = locator

	def setText(self, text):
		self.text = text

class CriticalRegion:
	def __init__(self, region, test, view):
		self.region = region
		self.text = view.substr(region)
		self.breached = False
		self.test = test

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

	def getTest(self):
		return self.test

class ProtectTestCommand(sublime_plugin.TextCommand): 
	def run(self, edit):
		global ID_REGIONS, TEST_FILE, TEST_SOUP, EDIT_FILE, NODE_REGIONS
		EDIT_FILE = str(self.view.file_name())
		try:
			htmlSoup = BeautifulSoup(open(EDIT_FILE), "lxml") #Open the html file
		except:
			print("There was an error opening the test file")
			e = sys.exc_info()[0]
			print(e)
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
				# self.view.window().run_command("split_and_open", fileMapping)
			except:
				TEST_SOUP = False
				print("There was an error locating the test file!")
				e = sys.exc_info()[0]
				print(e)
				return
		if TEST_SOUP: #Get all id selectors
			#getIDRegions(self.view) #This was used in attribute-based region identification
			getNodeRegions(self.view)

class SplitAndOpenCommand(sublime_plugin.WindowCommand):#This just creates a split-pane view with test/under_test
	def run(self, filePath):
		self.window.run_command("set_layout",{"cols": [0.0, 0.5, 1.0],"rows": [0.0, 1.0],"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
		self.window.focus_group(1)
		self.window.open_file(filePath)
		
class IDSelectorListener(sublime_plugin.EventListener):
	def on_selection_modified_async(self, view): #Triggered anytime the cursor moves or edit window is clicked
		if TEST_FILE and (EDIT_FILE == str(view.file_name())):
			if len(NODE_REGIONS) > 0:
				#print(NODE_REGIONS)
				printStatusOfEverything(view)
				caret_position = view.sel()[0]
				if caretBreachedCriticalRegion(caret_position, view) == True:
					print("Trigger Event!!")
			else:
				pass

	def on_modified_async(self,view):#Each time the buffer changes due to added character
		global NODE_REGIONS
		if TEST_FILE and (EDIT_FILE == str(view.file_name())) and LISTEN:
			NODE_REGIONS = []
			print("**Resetting Node Regions**\n")
			getNodeRegions(view)
		else:
			pass