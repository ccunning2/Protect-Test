class SeleniumTest:
	def __init__(self, locator, text):
		self.locator = locator
		self.text = text
		self.warn = True
		self.broken = False
		
	def getLocator(self):
		return self.locator

	def getText(self):
		return self.text

	def setLocator(self, locator):
		self.locator = locator

	def setText(self, text):
		self.text = text

class clickAndWait(SeleniumTest):
	def __init__(self, locator, text):
		super().__init__(locator, text)

class assertElementPresent(SeleniumTest):
	def __init__(self, locator, text):
		super().__init__(locator, text)

class select(SeleniumTest):
	def __init__(self, locator, text):
		super().__init__(locator, text)
		self.label = self.text.replace("label=", "")

class generalAssert(SeleniumTest):
	def __init__(self, locator, text):
		super().__init__(locator, text)	

		
		