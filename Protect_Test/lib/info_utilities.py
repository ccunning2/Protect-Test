from . import globals

def printRegionInfo(): #To print critical region information for debugging
	for crit_region in globals.NODE_REGIONS:
		print("Region locator: " + str(crit_region.getTest().getLocator()) + " Region:" + str(crit_region.region.a) + " thru " + str(crit_region.region.b))
	print('--------------\n')


def printStatusOfEverything(view):
	print("Listen is: " + str(globals.LISTEN) + "\n")
	print("Cursor is at: " + str(view.sel()[0].a) + "\n")
	#printRegionInfo()