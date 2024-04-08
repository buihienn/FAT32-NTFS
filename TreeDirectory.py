
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
        self.root = TreeNode("root", 5 ,0,0,0)
    
    def printRecursive(self, currentNode, depth):
        print('   ' * depth + currentNode.name + " " + str(currentNode.fileSize))
        for child in currentNode.children.values():
            self.printRecursive(child, depth + 1)

    def printTree(self):
        self.printRecursive(self.root, 0)