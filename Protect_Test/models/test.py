class SeleniumTest:
	def __init__(self, file, line, locator, text):
		self.file = file
		self.line = line
		self.locator = locator
		self.text = text
		self.warn = True
		self.broken = False
		self.region = None
		self.fold = True


class clickAndWait(SeleniumTest):
	def __init__(self, file, line, locator, text):
		super().__init__(file, line, locator, text)
		self.originalHREF = ""

class assertElementPresent(SeleniumTest):
	def __init__(self, file, line, locator, text):
		super().__init__(file, line, locator, text)

class select(SeleniumTest):
	def __init__(self, file, line, locator, text):
		super().__init__(file, line, locator, text)
		self.label = self.text.replace("label=", "")

class generalAssert(SeleniumTest):
	def __init__(self, file, line, locator, text):
		super().__init__(file, line, locator, text)	

class click(SeleniumTest):
	def __init__(self, file, line, locator, text):
		super().__init__(file, line, locator, text)

class type(SeleniumTest):
	def __init__(self, file, line, locator, text):
		super().__init__(file, line, locator, text)		

		
		