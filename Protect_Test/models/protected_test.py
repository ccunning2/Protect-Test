from . import file_under_test

class ProtectedTest:
	def __init__(self, path):
		self.path = path
		self.filesUnderTest = []

	def getFileUnderTest(self, path):
		for file in self.filesUnderTest:
			if file.path == path:
				return file
		newFile = file_under_test.FileUnderTest(path)
		self.filesUnderTest.append(newFile)
		return newFile