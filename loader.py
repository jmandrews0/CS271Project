import sys
import re

class WrongDimentions(Exception):
	pass

class Loader:
	def __init__(self, size, data=None):
		self.size = size
		if data is not None:
			self.data = data
			return
		self.data = []
		if len(sys.argv) > 1:
			self.loadFromFile(sys.argv[1])
		else:
			self.loadFromStdin()

	def loadFromFile(self, filename):
		with open(filename, 'r') as f:
			data = re.findall('[-0-9]+', f.read())

			if len(data) != self.size*self.size:
				raise WrongDimentions(
					f"Wrong dimentions. Expected {self.size}x{self.size} = {self.size*self.size}, got {len(data)} numbers")

			for i in range(self.size):
				arr = []
				for j in range(self.size):
					arr.append(int(data[i*self.size + j]) + 1)

				self.data.append(arr)

	def loadFromStdin(self):
		fName = input("Enter a file name:")
		self.loadFromFile(fName)

	def __getitem__(self, key):
		return self.data[key]


