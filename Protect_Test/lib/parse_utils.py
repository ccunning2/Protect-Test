from lxml import etree as ET
from lxml.html import document_fromstring
from lxml.html import parse as HTMLParse
from . import globals
import sublime, sublime_plugin
import re

def getTree(view): #Returns parse tree via lxmlimport(For use with XPath tasks)
	return ET.fromstring(view.substr(sublime.Region(0, view.size())))

def getViewTree(view): #Same as getTree?
	return document_fromstring(view.substr(sublime.Region(0, view.size())))

def getMasterTree(path): #Gets lxml etree from the file
	print(path)
	return HTMLParse(path)

def getTestFiles():
	list = []
	print('In getTestFiles\n')
	tree = getMasterTree()
	metaList = tree.findall('//meta')
	for element in metaList:
		if element.keys()[0] == 'test':
			list.append(element.get('test'))
	return list

def buildFormList(element): #Takes a form element, builds list of xpath locators to elements with 'required'
	set = element.findall('.//input[@required]')
	tree = element.getroottree()
	requiredList = []
	for el in set:
		requiredList.append(tree.getpath(el))
	return requiredList

def compareForms(list1): 
	print("IN COMPARE FORMS!!!\n")
	for selector in list1:
		print("Selector: " + str(selector) + "\n")
		if selector not in globals.ORIGINAL_FORM and selector not in globals.ELEMENTS_WARNED:
			print("ALERT-- New Required Field")
			sublime.message_dialog("You just added a required field that will break your test unless you modify it.")
			globals.ELEMENTS_WARNED.append(selector)

def getXPathElement(XPath, tree):
	return tree.xpath(XPath)

def getElement(locator, tree):
	if isXpath(locator):
		return getXPathElement(locator, tree)
	return getNonXPathElement(locator, tree)

def getElementCss(tag, key, value, tree):
	it = tree.iter()
	for element in it:
		if element.tag == tag and element.attrib[key] == value:
			return element
	return None

def getNonXPathElement(locator, tree):
	print('Getting non-XPath Element\n Locator: ' + locator)
	#Split locator
	splitLoc = locator.split('=', 1)
	type = splitLoc[0]
	if type == 'name':
		return getName(splitLoc[1], tree)
	elif type == 'link':
		return getLink(splitLoc[1], tree)
	elif type == 'css':
		#Need to do some string manipulation
		targets = splitLoc[1].split('[')
		tag = targets[0]
		attrib = targets[1].strip(']').split('=')
		key = attrib[0]
		value = attrib[1].strip('"')
		return getElementCss(tag, key, value, tree)
	return None

def getLink(name, tree): #Returns the first link element with 'name' from tree
	iterator = tree.iter()
	for element in iterator:
		if element.tag == 'a' and element.text == name:
			return element
	return None

def getName(name, tree): #Returns the first element with the 'name' attribute provided
	iterator = tree.iter()
	for element in iterator:
		if element.get('name') == name:
			return element
	return None

def findOption(test, tree):
	select = getElement(test.locator, tree)[0]
	it = select.iterdescendants()
	for element in it:
		if element.text == test.label:
			return select  #Returning the element here for use with the regions
	sublime.message_dialog("You just removed an option that will break your test!")
	test.warn = False
	return select

def verifyLocator(locator, tree): #Checks to see if element pointed to by locator is present
	#Is locator Xpath?
	print("In verify locator...")
	if isXpath(locator):
		if getXPathElement(locator, tree):
			return True
		return False
	else:
		if getNonXPathElement(locator, tree) is not None:
			print("Element located!")
			return True
		return False

def getClickWaitTarget(test, tree):
	if isXpath(test.locator):
		element = getElement(test.locator, tree)
	else:
		element = getNonXPathElement(test.locator, tree)

	if element is not None:
		if element.tag == 'a' and element.get('href') is not None:
			test.originalHREF = processTarget(element.get('href'))
			return processTarget(element.get('href'))
		elif element.getparent().tag == 'a' and element.getparent().get('href') is not None:
			test.originalHREF = processTarget(element.getparent().get('href'))
			return processTarget(element.getparent().get('href'))
		elif element.tag == 'input' and element.getparent().get('action') is not None:
			#Do we need to store the orignal action?
			return processTarget(element.getparent().get('action'))
		else:
			print("Could not locate element")

	else:
		print("Element not located")

def isXpath(locator):
	xPathPattern = '^//(\S+/?)*$'
	if re.match(xPathPattern, locator):
		return True
	else:
		return False

def processTarget(url):
	return url.replace("file://", "", 1)
