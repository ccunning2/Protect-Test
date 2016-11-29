import sublime
from . import globals

class CriticalRegion:
	def __init__(self, region, test, view):
		self.region = region
		self.text = view.substr(region)
		self.breached = False
		self.test = test
		self.modified = False

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

# 	for crit_region in globals.NODE_REGIONS:
# 		if crit_region.region.contains(point):
# 			print("Hovering over critical region")
# 			view.show_popup(getTestHtml(crit_region), sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 700,700,None,None)

# def getTestHtml(crit_region):
# 	test = crit_region.test
# 	modified = str(crit_region.modified)
# 	html = "<html><body><h3>Test Info:</h3><ul><li>Test Type: " + test.test + "</li><li>Test Locator: " + test.locator + "</li><li>Modified: " + modified + "</ul></body></html>"
# 	return html

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
	print(beginLine)
	print(openTag)
	print(closeTag)
	startPos1 = view.text_point(beginLine-1, 0)
	openTagRegion = view.find(openTag, startPos1, sublime.IGNORECASE)
	startPos2 = openTagRegion.b
	closeTagRegion = view.find(closeTag, startPos2, sublime.IGNORECASE)
	regionBegin = openTagRegion.a
	regionEnd = closeTagRegion.b
	return sublime.Region(regionBegin, regionEnd)
	#globals.NODE_REGIONS.append(CriticalRegion(region,test,view))

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