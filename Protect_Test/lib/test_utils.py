from . import globals
from . import parse_utils
from ..models import test
import sublime, sublime_plugin

def buildTestData(): #Retrieves all test data from testfile
	rows = globals.TEST_SOUP.find_all('tr')
	testList = []
	#Get rid of first two rows
	rows.pop(0)
	rows.pop(0)
	for row in rows:
		tempData = row.find_all('td')
		type = tempData[0].text
		if type == "clickAndWait":
			testData = test.clickAndWait(tempData[1].text, tempData[2].text)
		elif type == "assertElementPresent":
			testData = test.assertElementPresent(tempData[1].text, tempData[2].text)
		elif type == "select":
			testData = test.select(tempData[1].text, tempData[2].text)
		else:
			testData = test.SeleniumTest(tempData[1].text, tempData[2].text)
		testList.append(testData)
	return testList

#Initial test processing done when command is run
def processTestsInitial(testList):
	tree = parse_utils.getMasterTree()
	for test in testList:
		print(test)
		if test.__class__.__name__ == "clickAndWait":
			try:
				processForm(test.locator, tree)
			except IndexError:
				print("Invalid Syntax, skipping for now")
		elif test.__class__.__name__ == "assertElementPresent":
			parse_utils.getElement(test.locator, tree)
		elif test.__class__.__name__ == "select":
			parse_utils.findOption(test, tree)
		else:
			#Just add the selector to the list of test selectors for now
			globals.CRITICAL_SELECTORS.append(test.locator)

#Done everytime the listener is triggered.
def processTests(testList, tree):
	for test in testList:
		if test.__class__.__name__ == "clickAndWait":
			processForm(test.locator, tree)
		elif test.__class__.__name__ == "assertElementPresent":
			element = parse_utils.getElement(test.locator, tree)
			if not element:
				sublime.message_dialog("You've just made an edit that will cause your test to fail."
				"The parser cannot find " + test.locator + ","
				" but you may have removed another element to cause this.")
		elif test.__class__.__name__ == "select":
			parse_utils.findOption(test, tree)
		else:
			print("Test type not implemented.")
			
def processForm(XPathLocator, tree):
	requiredList = None
	button = tree.xpath(XPathLocator)[0]
	it = button.iterancestors()
	for element in it:
		if element.tag == "form":
			if globals.ORIGINAL_FORM is None:
				globals.ORIGINAL_FORM = parse_utils.buildFormList(element)
				globals.CRITICAL_SELECTORS.append(element)
			else:
				requiredList = parse_utils.buildFormList(element)
			break
	if globals.ORIGINAL_FORM is None and requiredList is None:
		print('Input has no form parent!!')
	if requiredList is not None:
		print("requiredList is: " + str(requiredList))
		parse_utils.compareForms(requiredList) 
	else:
		print("No requiredList")
	if globals.ORIGINAL_FORM is not None:
		print("globals.ORIGINAL_FORM is: " + str(globals.ORIGINAL_FORM))
	else:
		print("No globals.ORIGINAL_FORM")

# def idSelectors(): #Retrieves all 'id' selectors from testfile. globals.TEST_SOUP is a BeautifulSoup object
# 	testTableData = globals.TEST_SOUP.find_all('td')
# 	idList = []
# 	for data in testTableData:
# 		if str(data.string).startswith('id',0,2):
# 			idList.append(data.string[3:]) #In a selector 'id=something, the something begins at position 3'
# 	return idList