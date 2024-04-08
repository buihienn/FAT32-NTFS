
class TreeNode:
    def __init__(self, nameEntry, idEntry):
        self.name = nameEntry
        self.id = idEntry
        self.children = {}

class TreeDirectory:
    def __init__(self):
        self.root = TreeNode("root", 5)
    
    def printRecursive(self, currentNode, depth):
        print('   ' * depth + currentNode.name + " " + str(currentNode.id))
        for child in currentNode.children.values():
            self.printRecursive(child, depth + 1)

    def printTree(self):
        self.printRecursive(self.root, 0)