import sublime, sublime_plugin
from bs4 import BeautifulSoup

def idSelectors(testSoup): #testSoup is a BeautifulSoup object
	testTableData = testSoup.find_all('td')
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
		selectorRegions = view.find_all(searchString)
		for region in selectorRegions:
			regions.append(region)
	return regions

def highlightRegions(view, regions):
	view.add_regions('ThreatenedTestIDs', regions, "invalid", "", 0)

class ProtectTestCommand(sublime_plugin.TextCommand): 
	def run(self, edit):
		fileName = str(self.view.file_name())
		try:
			htmlSoup = BeautifulSoup(open(fileName), "lxml") #Open the html file
		except:
			print("There was an error opening the test file")
			return
		try:
			testFile = htmlSoup.meta['test'] #Look for html tag specifying location of test file, if applicable
			file = True
		except KeyError:
			testFile = "ERROR: No test file identified." 
			file = False

		if file: #If we have a meta tag with a test attribute, look for the test file
			try: 
				testSoup = BeautifulSoup(open(testFile), "lxml")
			except:
				testSoup = False
				print("There was an error locating the test file!")
				return
		if testSoup: #Get all id selectors
			idList = idSelectors(testSoup)
			regions = getRegions(self.view, 'id', idList)
			highlightRegions(self.view, regions)


