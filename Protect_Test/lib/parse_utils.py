from lxml import etree as ET
from lxml.html import document_fromstring
from lxml.html import parse as HTMLParse
from . import globals
import sublime

def getTree(view): #Returns parse tree via lxmlimport(For use with XPath tasks)
	return ET.fromstring(view.substr(sublime.Region(0, view.size())))

def getViewTree(view): #Same as getTree?
	return document_fromstring(view.substr(sublime.Region(0, view.size())))

def getMasterTree(): #Gets lxml etree from the file
	return HTMLParse(open(globals.EDIT_FILE))

def buildFormList(element): #Takes a form element, builds list of xpath locators to elements with 'required'
	set = element.findall('.//input[@required]')
	tree = element.getroottree()
	requiredList = []
	for el in set:
		requiredList.append(tree.getpath(el))
	return requiredList

def compareForms(list1):
	for selector in list1:
		if selector not in globals.ORIGINAL_FORM and selector not in globals.ELEMENTS_WARNED:
			print("ALERT-- New Required Field")
			sublime.message_dialog("You just added a required field that will break your test unless you modify it.")
			globals.ELEMENTS_WARNED.append(selector)