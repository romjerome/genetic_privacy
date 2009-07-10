import utils

class Node(utils.Struct):
	def __init__(self, id):
		self.id = id
		self.mom = None
		self.dad = None
		self.sex = None
		self.spouses = set()
		self.children = set()

	@property
	def parents(self):
		return (self.dad, self.mom)


