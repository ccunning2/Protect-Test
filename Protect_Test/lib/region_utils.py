import sublime
from . import globals, parse_utils

class CriticalRegion:
	def __init__(self, region, test, view):
		self.region = region
		self.text = view.substr(region)
		self.test = test
		self.modified = False


def pointInCriticalRegion(point, view):
	for test in globals.ACTIVE_FILE.tests:
		if test.region is not None and test.region.contains(point):
			print("Hovering over critical region")
			view.show_popup(getTestHtml(test), sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 700,700,disableFolding,None)

def getTestHtml(test):
	if test.fold:
		html = "" + \
		"<html>" + \
		"<body>" + \
			"<h3>Test Info:</h3>" + \
			"<ul>" + \
				"<li>Test Type: " + test.__class__.__name__ + "</li>" + \
				"<li>Test Locator: " + test.locator + "</li>" + \
				"<li>Test File: " + test.file.path + "</li>" + \
				"<li>Line Number: " + str(test.line) + "</li>" + \
				"<li>Test Broken: " + str(test.broken) + "</li>" + \
			"</ul>" + \
		"<h5>To disable folding for this test, <a href=\"" + str(test) + "\">click here</a></h5>" + \
		"</body>" + \
		"</html>"
	else:
		html = "" + \
		"<html>" + \
		"<body>" + \
			"<h3>Test Info:</h3>" + \
			"<ul>" + \
				"<li>Test Type: " + test.__class__.__name__ + "</li>" + \
				"<li>Test Locator: " + test.locator + "</li>" + \
				"<li>Test File: " + test.file.path + "</li>" + \
				"<li>Line Number: " + str(test.line) + "</li>" + \
				"<li>Test Broken: " + str(test.broken) + "</li>" + \
			"</ul>" + \
		"<h5>To enable folding for this test, <a href=\"" + str(test) + "\">click here</a></h5>" + \
		"</body>" + \
		"</html>"
	return html

def disableFolding(test_to_disable):
	for test in globals.ACTIVE_FILE.tests:
		if str(test) == str(test_to_disable):
			test.fold = not test.fold
			#Unfold Region here?

# def getRegionByLines(line1, line2, view): #Returns the region starting at the beginning of line1 and the end of line 2 
# 	a = view.text_point(line1-1, 0)
# 	lastCol = view.line(view.text_point(line2-1, 0)).b
# 	return sublime.Region(a, lastCol)

# def getRegions(view, selectorType, selectors): #Return an array of the regions to be highlighted
# 	regions = []
# 	for selector in selectors:
# 		searchString = selectorType + "=" + "\"" + selector + "\""
# 		print(searchString)
# 		selectorRegions = view.find_all(searchString) # add 'ignore case' flag
# 		for region in selectorRegions:
# 			critRegion = CriticalRegion(region, view)
# 			regions.append(critRegion)
# 	return regions

def createRegion(element, etree, view):
	beginLine = element.sourceline
	tag = element.tag
	closeTag = "</" + tag + ">"
	openTag = "<" + tag 
	noCloseEnd = ">"
	startPos1 = view.text_point(beginLine-1, 0)
	openTagRegion = view.find(openTag, startPos1, sublime.IGNORECASE)
	startPos2 = openTagRegion.b
	if tag in globals.NO_CLOSE_TAG:
		closeTagRegion = view.find(noCloseEnd, startPos2, sublime.IGNORECASE)
	else:
		closeTagRegion = view.find(closeTag, startPos2, sublime.IGNORECASE)
	regionBegin = openTagRegion.a
	regionEnd = closeTagRegion.b
	return sublime.Region(regionBegin, regionEnd)

def setRegion(test, tree, view):
	element = parse_utils.getElement(test.locator, tree)
	if element is not None:
		test.region = createRegion(element, tree, view)
	else:
		sublime.error_message("Could not locate element at: " + test.locator)

def updateRegions(view):
	tree = parse_utils.getViewTree(view)
	for crit_region in globals.REGION_LIST:
		element = parse_utils.getElement(crit_region.test.locator, tree)[0]
		print(element)
		crit_region.region = createRegion(element, tree, view)
	

# def highlightRegions(view, regions):
# 	print("Highlighting Regions\n")
# 	regionList = []
# 	for region in regions:
# 		regionList.append(region.getRegion())
# 	view.add_regions('CritRegions', regionList, "invalid", "", 0)

# def caretInRegion(region, caret_position):
# 	start = region.getRegion().a
# 	end = region.getRegion().b
# 	position = caret_position.a
# 	if position >= start and position <= end:
# 		return True
# 	else:
# 		return False

# def caretBreachedCriticalRegion(caret_position, view): #If returns true, we have entered and exited a critical region
# 	for region in globals.NODE_REGIONS:
# 		if caretInRegion(region, caret_position):
# 			print("Region Breach!\n")
# 			region.breach()
# 			globals.LISTEN = False
# 		if not caretInRegion(region, caret_position) and region.beenBreached():
# 			if region.getText() != view.substr(region.getRegion()):
# 				print("CHANGE!!!")
# 				region.modified = True
# 				sublime.message_dialog("You just made a change that will potentially break your test file!")
# 			region.reset() #Modify this to reset region text?
# 			globals.LISTEN = True #Resume listening
# 			return True
# 	return False