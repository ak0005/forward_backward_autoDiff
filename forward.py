import ast
import math
import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

smallNum = 1e-16


class dual:
    def __init__(self, realPart, DualPart=0):
        self.fi = realPart
        self.sc = DualPart

    def printIt(self):
        print(self.fi, self.sc)


def add(a, b):
    return dual(a.fi+b.fi, a.sc+b.sc)


def sub(a, b):
    return dual(a.fi-b.fi, a.sc-b.sc)


def mul(a, b):
    return dual(a.fi*b.fi, a.fi*b.sc + a.sc*b.fi)


def div(a, b):
    return dual(a.fi/(smallNum+b.fi), (a.sc*b.fi - a.fi*b.sc)/(smallNum+b.fi*b.fi))


def pow(a, b):
    return dual(math.pow(a.fi, b.fi), math.pow(a.fi, b.fi)*(b.sc*math.log(smallNum+a.fi) + (a.sc*b.fi)/(smallNum+a.fi)))


def sin(a):
    return dual(math.sin(a.fi), a.sc*math.cos(a.fi))


def cos(a):
    return dual(math.cos(a.fi), -a.sc*math.sin(a.fi))


def tan(a):
    return dual(math.tan(a.fi), a.sc/(smallNum+math.cos(a.fi)**2))


def log(a):
    return dual(math.log(smallNum+a.fi), a.sc/(smallNum+a.fi))


def sinh(a):
    return dual(math.sinh(a.fi), a.sc*math.cosh(a.fi))


def cosh(a):
    return dual(math.cosh(a.fi), a.sc*math.sinh(a.fi))


functionDict = {
    'Sub': sub,
    'Add': add,
    'Div': div,
    'Mult': mul,
    'Pow': pow,
    'log': log,
    'sin': sin,
    'cos': cos,
    'tan': tan,
    'sinh': sinh,
    'cosh': cosh
}


class Node:
    def __init__(self):
        self.isConstant = False
        self.isVariable = False
        self.isFunc = False
        self.isBinary = False

        self.func = None
        self.value = dual(0, 0)
        self.varId = None

    def makeItConstant(self, value):
        self.isConstant = True
        self.value = dual(value, 0)

    def makeItVariable(self, varId):
        self.isVariable = True
        self.varId = varId

    def makeItFunction(self, func, isBinary):
        self.isFunc = True
        self.func = func
        self.isBinary = isBinary


print('This Script supports:-')
print('****Case Sensitive and Angles are in Radian****')
print('sin as \'sin\'')
print('cos as \'cos\'')
print('tan as \'tan\'')
print('sin hyperbolic as \'sinh\'')
print('cos hyperbolic as \'cosh\'')
print('log base e as \'log\'')
print('addition as \'+\'')
print('subtraction as \'-\'')
print('multiplication as \'*\'')
print('division as \'/\'')
print('power as \'**\'')
print('variable name constrained are same as that of python')
print()

expression = input("Enter your Expression: ")
t = ast.parse(expression, mode='eval')

varDict = {}
nodes = []
tree = []
nodesAtLevel = []


def createExpressionTree(node, depth):
    while len(nodesAtLevel) <= depth:
        nodesAtLevel.append([])

    if isinstance(node, ast.BinOp):
        if node.op.__class__.__name__ not in functionDict:
            raise Exception(node.op.__class__.__name__ +
                            ' not suported binary function')

        currentNode = Node()
        currentNode.makeItFunction(
            functionDict[node.op.__class__.__name__], isBinary=True)

        ind = len(nodes)
        nodesAtLevel[depth].append(ind)
        nodes.append(currentNode)
        tree.append([])
        tree[ind].append(createExpressionTree(node.left, depth+1))
        tree[ind].append(createExpressionTree(node.right, depth+1))

        return ind

    elif isinstance(node, ast.Call):
        if node.func.id not in functionDict:
            raise Exception(node.func.id+' not suported unary function')

        currentNode = Node()
        currentNode.makeItFunction(functionDict[node.func.id], isBinary=False)

        ind = len(nodes)
        nodesAtLevel[depth].append(ind)
        nodes.append(currentNode)
        tree.append([])
        tree[ind].append(createExpressionTree(node.args[0], depth+1))

        return ind

    elif isinstance(node, ast.Name):
        if node.id in varDict:
            ind = varDict[node.id]
        else:
            currentNode = Node()
            currentNode.makeItVariable(node.id)
            ind = len(nodes)
            nodesAtLevel[depth].append(ind)
            nodes.append(currentNode)
            tree.append([])
            varDict[node.id] = ind

        return ind

    elif isinstance(node, ast.Constant):
        currentNode = Node()
        currentNode.makeItConstant(node.value)
        ind = len(nodes)
        nodesAtLevel[depth].append(ind)
        nodes.append(currentNode)
        tree.append([])

        return ind


createExpressionTree(t.body, 0)

for k, v in varDict.items():
    val = input("Enter value for Variable "+k+" :")
    nodes[v].value = dual(float(val))


def handleNode(ind):
    currentNode = nodes[ind]

    if currentNode.isConstant or currentNode.isVariable:
        return

    if currentNode.isBinary:
        vall = nodes[tree[ind][0]].value
        valr = nodes[tree[ind][1]].value

        currentNode.value = currentNode.func(vall, valr)

    else:
        currentNode.value = currentNode.func(nodes[tree[ind][0]].value)


def evaluate():
    for i in range(len(nodesAtLevel)-1, -1, -1):
        for nodeIn in nodesAtLevel[i]:
            handleNode(nodeIn)

    return nodes[0].value


print()
for k, v in varDict.items():
    nodes[v].value = dual(nodes[v].value.fi, 1)
    print('derivative wrt '+k+' '+str(evaluate().sc))
    nodes[v].value = dual(nodes[v].value.fi)


# print(tree)
# def printTree(ind):
#     currentNode = nodes[ind]
#     print(ind)

#     if currentNode.isConstant:
#         print('constant')
#         currentNode.value.print()
#         print()

#     elif currentNode.isVariable:
#         print(currentNode.varId)
#         print()

#     elif currentNode.isBinary:
#         print(currentNode.func.__name__)
#         print()
#         printTree(tree[ind][0])
#         printTree(tree[ind][1])

#     else:
#         print(currentNode.func.__name__)
#         print()
#         printTree(tree[ind][0])

# printTree(0)
