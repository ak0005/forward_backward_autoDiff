import ast
import math
import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

smallNum = 1e-16


def add(a, b, isDerivative=False, isRight=False):
    if isDerivative:
        return 1
    else:
        return a+b


def sub(a, b, isDerivative=False, isRight=False):
    if isDerivative:
        if isRight:
            return -1
        else:
            return 1
    else:
        return a-b


def mul(a, b, isDerivative=False, isRight=False):
    if isDerivative:
        if isRight:
            return a
        else:
            return b
    else:
        return a*b


def div(a, b, isDerivative=False, isRight=False):
    if isDerivative:
        if isRight:
            return -a/(smallNum+b*b)
        else:
            return 1/(smallNum+b)
    return a/(smallNum+b)


def pow(a, b, isDerivative=False, isRight=False):
    if isDerivative:
        if isRight:
            return math.pow(a, b)*math.log(smallNum+a)
        else:
            return math.pow(a, b-1)*b
    else:
        return math.pow(a, b)


def sin(a, isDerivative=False):
    if isDerivative:
        return math.cos(a)
    else:
        return math.sin(a)


def cos(a, isDerivative=False):
    if isDerivative:
        return -1*math.sin(a)
    else:
        return math.cos(a)


def tan(a, isDerivative=False):
    if isDerivative:
        return 1/(smallNum+math.cos(a)**2)
    else:
        return math.tan(a)


def log(a, isDerivative=False):
    if isDerivative:
        return 1/(smallNum+a)
    else:
        return math.log(smallNum+a)


def sinh(a, isDerivative=False):
    if isDerivative:
        return math.cosh(a)
    else:
        return math.sinh(a)


def cosh(a, isDerivative=False):
    if isDerivative:
        return math.sinh(a)
    else:
        return math.cosh(a)


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
        self.value = 0
        self.gradient = 0
        self.varId = None

    def makeItConstant(self, value):
        self.isConstant = True
        self.value = value

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
    nodes[v].value = float(val)


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


def evaluateForward():
    k = 0
    for i in range(len(nodesAtLevel)-1, -1, -1):
        for nodeIn in nodesAtLevel[i]:
            handleNode(nodeIn)
            k += 1

    return nodes[0].value


# forward pass
evaluateForward()


# backward pass
def handleNode2(ind):
    currentNode = nodes[ind]

    if currentNode.isConstant or currentNode.isVariable:
        return

    if currentNode.isBinary:
        vall = nodes[tree[ind][0]].value
        valr = nodes[tree[ind][1]].value

        gl = currentNode.func(vall, valr, True, False)
        gr = currentNode.func(vall, valr, True, True)

        nodes[tree[ind][0]].gradient += gl*currentNode.gradient
        nodes[tree[ind][1]].gradient += gr*currentNode.gradient
    else:
        val = nodes[tree[ind][0]].value
        nodes[tree[ind][0]].gradient += currentNode.func(
            val, True) * currentNode.gradient


def evaluateBackward():
    nodes[0].gradient = 1  # seed

    for i in range(0, len(nodesAtLevel)):
        for nodeIn in nodesAtLevel[i]:
            handleNode2(nodeIn)


evaluateBackward()

print()
for k, v in varDict.items():
    print('derivative wrt '+k+' '+str(nodes[v].gradient))
