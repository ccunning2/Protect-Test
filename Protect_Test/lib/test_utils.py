from . import globals
from . import parse_utils, region_utils, info_utilities
from ..models import test, file_under_test
import sublime, sublime_plugin, os.path
import re

def buildTestData(): #Retrieves all test data from testfile
	print('In build test data\n')
	testList = []
	for protected_test in globals.PROTECTED_TESTS:
		print(protected_test.path)
		testTree = parse_utils.HTMLParse(protected_test.path)
		rows = testTree.findall('//tr')
		#Get rid of first row
		rows.pop(0)
		testedFile = None
		for row in rows:
			tempData = row.getchildren()
			type = tempData[0].text
			if type == "open":
				target = parse_utils.processTarget(tempData[1].text)
				if not filePresent(target):
					sublime.message_dialog("The target of test " + protected_test.path + ", " + target + ", cannot be found!")
					continue
				testedFile = protected_test.getFileUnderTest(target)
			elif type == "clickAndWait": #Need to resolve target of clickAndWait to get next "FileUnderTest"
				testData = test.clickAndWait(testedFile, tempData[0].sourceline, tempData[1].text, tempData[2].text)
				testedFile.tests.append(testData)
				#Resolve target file of clickAndWait, if applicable
				testedFileTree = parse_utils.HTMLParse(testedFile.path)
				target = parse_utils.getClickWaitTarget(testData, testedFileTree)
				if target is None:
					sublime.error_message("ERROR IN PROTECTED TEST: " + protected_test.path + "\nThere was an error determining target " + testData.locator + " in file " + testedFile.path)
					continue
				print("ClickWait target is " + target)
				if testedFile.path != target:
					testedFile = protected_test.getFileUnderTest(target)
			elif type == "click":
				testData = test.click(testedFile, tempData[0].sourceline, tempData[1].text, tempData[2].text)
				testedFile.tests.append(testData)
			elif type == "assertElementPresent":
				testData = test.assertElementPresent(testedFile, tempData[0].sourceline, tempData[1].text, tempData[2].text)
				testedFile.tests.append(testData)
			elif type == "select":
				testData = test.select(testedFile, tempData[0].sourceline, tempData[1].text, tempData[2].text)
				testedFile.tests.append(testData)
			elif type in globals.ASSERT_TESTS:
				testData = test.generalAssert(testedFile, tempData[0].sourceline, tempData[1].text, tempData[2].text)
				testedFile.tests.append(testData)
			elif type in globals.IGNORE_TESTS:
				continue
			else:
				testData = test.SeleniumTest(testedFile, tempData[0].sourceline, tempData[1].text, tempData[2].text)
				testedFile.tests.append(testData)
			#testList.append(testData)
	

#Initial test processing done when plugin is loaded
def verifyTestsInitial():
	for protected_test in globals.PROTECTED_TESTS:
		for file in protected_test.filesUnderTest:
			tree = parse_utils.getMasterTree(file.path)
			for test in file.tests:
				print(test)
				if not parse_utils.verifyLocator(test.locator, tree):
					sublime.message_dialog("Cannot locate element at " + test.locator)
				if test.__class__.__name__ == "clickAndWait": #TODO Add region for this
					try:
						processForm(test.locator, tree, test, file)
					except IndexError:
						print("Invalid Syntax, skipping for now")
				elif test.__class__.__name__ == "select":
					element = parse_utils.findOption(test, tree)
					# region = region_utils.createRegion(element, tree, view)
					# region = region_utils.CriticalRegion(region, test, view)
					# globals.REGION_LIST.append(region)
				else:
					if parse_utils.isXpath(test.locator):
						element = parse_utils.getElement(test.locator, tree)[0]
					else:
						element = parse_utils.getNonXPathElement(test.locator, tree)
					# region = region_utils.createRegion(element, tree, view)
					# region = region_utils.CriticalRegion(region, test, view)
					# globals.REGION_LIST.append(region)

#Done everytime the listener is triggered.
def processTests(testList, tree, view, file):
	for test in testList:
		if test.warn:
			if test.__class__.__name__ == "clickAndWait":
				if not parse_utils.verifyLocator(test.locator, tree):
					queryWarning(test,view)
				else:
					processForm(test.locator, tree, test, file)
				if test.originalHREF != "" and test.warn:
					checkClickWaitTarget(test, tree, view)
			elif test.__class__.__name__ == "click":
				if not parse_utils.verifyLocator(test.locator, tree):
					queryWarning(test, view)
			elif test.__class__.__name__ == "assertElementPresent":
				element = parse_utils.getElement(test.locator, tree)
				if not element:
					queryWarning(test, view)
			elif test.__class__.__name__ == "select":
				parse_utils.findOption(test, tree)
				if not parse_utils.verifyLocator(test.locator, tree):
					queryWarning(test, view)
			elif test.__class__.__name__ == "generalAssert":
				if not parse_utils.verifyLocator(test.locator, tree):
					queryWarning(test, view)
				element = parse_utils.getElement(test.locator, tree)[0]
				if element.text.strip() != test.text.strip():
					queryWarning(test, view)
			else:
				print("Test type not implemented.")
			
def processForm(locator, tree, test, file):
	requiredList = None
	print(locator)
	if parse_utils.isXpath(locator):
		button = tree.xpath(locator)[0]
	else:
		button = parse_utils.getNonXPathElement(locator, tree)
	it = button.iterancestors()
	for element in it:
		if element.tag == "form":
			if file.ORIGINAL_FORM is None:
				file.ORIGINAL_FORM = parse_utils.buildFormList(element)
				# region = region_utils.createRegion(element, tree, view)
				# globals.REGION_LIST.append(region_utils.CriticalRegion(region, test, view))
			else:
				requiredList = parse_utils.buildFormList(element)
			break
	if file.ORIGINAL_FORM is None and requiredList is None:
		print('Input has no form parent!!')
	if requiredList is not None:
		print("requiredList is: " + str(requiredList))
		parse_utils.compareForms(requiredList) 
	else:
		print("No requiredList")
	if file.ORIGINAL_FORM is not None:
		print("file.ORIGINAL_FORM is: " + str(file.ORIGINAL_FORM))
	else:
		print("No file.ORIGINAL_FORM")

def filePresent(path):
	return os.path.isfile(path)

def queryWarning(test, view):
	answer = sublime.yes_no_cancel_dialog("The element pointed at " + test.locator + " has changed, potentially breaking your test. If you'd like to continue being warned about this test, hit cancel.", "Turn off warnings for this test.", "Undo changes")
	if answer == sublime.DIALOG_YES:
		test.warn = False
	if answer == sublime.DIALOG_NO:
		view.run_command("undo")
		

def checkClickWaitTarget(test, tree, view):
	if test.warn:	
		if parse_utils.isXpath(test.locator):
			element = parse_utils.getElement(test.locator, tree)
		else:
			element = parse_utils.getNonXPathElement(test.locator, tree)

		if element is not None:
			if element.tag == 'a' and element.get('href') is not None:
				if test.originalHREF != parse_utils.processTarget(element.get('href')):
					queryWarning(test, view)
			elif element.getparent().tag == 'a' and element.getparent().get('href') is not None:
				if test.originalHREF != parse_utils.processTarget(element.getparent().get('href')):
					queryWarning(test, view)
			elif element.tag == 'input' and element.getparent().get('action') is not None:
				#Deal with modified action attribute?
				pass
			else:
				print("Could not locate element")
		else:
			print("Element not located")

# def idSelectors(): #Retrieves all 'id' selectors from testfile. globals.TEST_SOUP is a BeautifulSoup object
# 	testTableData = globals.TEST_SOUP.find_all('td')
# 	idList = []
# 	for data in testTableData:
# 		if str(data.string).startswith('id',0,2):
# 			idList.append(data.string[3:]) #In a selector 'id=something, the something begins at position 3'
# 	return idList