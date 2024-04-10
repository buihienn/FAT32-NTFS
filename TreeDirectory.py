
class TreeNode:
    def __init__(self, nameEntry, idEntry,fileSize, dateCreated, dateModified):
        self.name = nameEntry
        self.id = idEntry
        self.fileSize = fileSize
        self.dateCreated = dateCreated
        self.dateModified = dateModified
        self.children = {}

class TreeDirectory:
    def __init__(self):
        self.root = TreeNode("Main", 5 ,0,0,0)
    
    def printRe(self, currentNode, depth):
        print('   ' * depth + currentNode.name + " " + str(currentNode.id))
        for child in currentNode.children.values():
            self.printRe(child, depth + 1)

    def printTree(self):
        self.printRe(self.root, 0)