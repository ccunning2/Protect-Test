from . import globals
from . import parse_utils, region_utils
from ..models import test
import sublime, sublime_plugin

def buildTestData(): #Retrieves all test data from testfile
	print('In build test data\n')
	testList = []
	for file in globals.TEST_FILES:
		print(file)
		tree = parse_utils.HTMLParse(file)
		rows = tree.findall('//tr')
		#Get rid of first two rows
		rows.pop(0)
		rows.pop(0)
		for row in rows:
			tempData = row.getchildren()
			type = tempData[0].text
			if type == "clickAndWait":
				testData = test.clickAndWait(file, tempData[0].sourceline, tempData[1].text, tempData[2].text)
			elif type == "click":
				testData = test.click(file, tempData[0].sourceline, tempData[1].text, tempData[2].text)
			elif type == "assertElementPresent":
				testData = test.assertElementPresent(file, tempData[0].sourceline, tempData[1].text, tempData[2].text)
			elif type == "select":
				testData = test.select(file, tempData[0].sourceline, tempData[1].text, tempData[2].text)
			elif type in globals.ASSERT_TESTS:
				testData = test.generalAssert(file, tempData[0].sourceline, tempData[1].text, tempData[2].text)
			elif type in globals.IGNORE_TESTS:
				continue
			else:
				testData = test.SeleniumTest(file, tempData[0].sourceline, tempData[1].text, tempData[2].text)
			testList.append(testData)
	return testList

#Initial test processing done when command is run
def processTestsInitial(testList, view):
	tree = parse_utils.getMasterTree()
	for test in testList:
		print(test)
		if not parse_utils.verifyLocator(test.locator, tree):
			sublime.message_dialog("Cannot locate element at " + test.locator)
		if test.__class__.__name__ == "clickAndWait": #TODO Add region for this
			try:
				processForm(test.locator, tree, test, view)
			except IndexError:
				print("Invalid Syntax, skipping for now")
		elif test.__class__.__name__ == "select":
			element = parse_utils.findOption(test, tree)
			region = region_utils.createRegion(element, tree, view)
			region = region_utils.CriticalRegion(region, test, view)
			globals.REGION_LIST.append(region)
		else:
			if parse_utils.isXpath(test.locator):
				element = parse_utils.getElement(test.locator, tree)[0]
			else:
				element = parse_utils.getNonXPathElement(test.locator, tree)
			region = region_utils.createRegion(element, tree, view)
			region = region_utils.CriticalRegion(region, test, view)
			globals.REGION_LIST.append(region)

#Done everytime the listener is triggered.
def processTests(testList, tree, view):
	for test in testList:
		if test.warn:
			if test.__class__.__name__ == "clickAndWait":
				processForm(test.locator, tree, test, view)
			elif test.__class__.__name__ == "assertElementPresent":
				element = parse_utils.getElement(test.locator, tree)
				if not element:
					sublime.message_dialog("You've just made an edit that will cause your test to fail."
					"The parser cannot find " + test.locator + ","
					" but you may have removed another element to cause this.")
					test.warn = False
					test.broken = True
			elif test.__class__.__name__ == "select":
				parse_utils.findOption(test, tree)
			elif test.__class__.__name__ == "generalAssert":
				element = parse_utils.getElement(test.locator, tree)[0]
				if element.text.strip() != test.text.strip():
					sublime.message_dialog("You just altered text used in an assertion that will break your test.")
					print("Test text: " + test.text.strip())
					print("Element text: " + element.text.strip())
					test.warn = False
					test.broken = True
			else:
				print("Test type not implemented.")
			
def processForm(locator, tree, test, view):
	requiredList = None
	print(locator)
	if parse_utils.isXpath(locator):
		button = tree.xpath(locator)[0]
	else:
		button = parse_utils.getNonXPathElement(locator, tree)
	it = button.iterancestors()
	for element in it:
		if element.tag == "form":
			if globals.ORIGINAL_FORM is None:
				globals.ORIGINAL_FORM = parse_utils.buildFormList(element)
				region = region_utils.createRegion(element, tree, view)
				globals.REGION_LIST.append(region_utils.CriticalRegion(region, test, view))
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