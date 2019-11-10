import math
import heapq

"------------------------------------------------------------------------------"
# each cell in the board should contain a Variable
class Variable:
    # Domain for the variable
    domain = set()
    # The value of the variable 0 means no assignment
    value = 0
    # The x and y axis location of this variable
    position = (0,0)
    
    def __init__(self, value, x, y):
        self.value = value
        self.position = (x,y)

    def __lt__(self, other):
        return len(self.domain) < len(other.domain)
    def __le__(self, other):
        return len(self.domain) <= len(other.domain)
    def __eq__(self, other):
        return len(self.domain) == len(other.domain)
    def __ne__(self, other):
        return len(self.domain) != len(other.domain)
    def __gt__(self, other):
        return len(self.domain) > len(other.domain)
    def __ge__(self, other):
        return len(self.domain) >= len(other.domain)
    def __hash__(self):
        return self.position[0] + 25*self.position[1]

"------------------------------------------------------------------------------"
class sudokuSolver:
    
    # The board will be a 2 dimensional array
    board = []
    # the variable heap/queue will be a list of variable objects sorted as a heap
    varHeap = []
    # For each value 1-25, a set of variables that cannot be that value
    constraintArr = []
    # the 1 dimensional size of the board
    size = 0
    # a set of all possible values a variable could have
    allValues = set()
    # boolean value identifying if the problem is solved yet
    solved = False
    
    def __init__(self, board, size = 25):
        self.size = size
        self.allValues = set(i for i in range(1,size+1))
        # initialize constraintArr
        for i in range(size):
            self.constraintArr.append(set())
        # initialize the board with Variable objects in each cell
        for x in range(size):
            self.board.append([])
            for y in range(size):
                self.board[-1].append(Variable(board[x][y],x,y))
                if self.board[-1][-1].value == 0:
                    self.varHeap.append(self.board[-1][-1])
    
    # returns constraints from this variables row
    def rowConstraints(self, y) -> set:
        con = set()
        for x in range(len(self.board)):
            con.add(self.board[x][y].value)
        return con
            
     
    # returns constraints from this variables column
    def colConstraints(self, x) -> set:
        con = set()
        for y in range(len(self.board[0])):
            con.add(self.board[x][y].value)
        return con

    # returns constraints from this variables box
    def boxConstraints(self, x, y) -> set:
        # iterate through all cells in the box for this Variable
        con = set()
        cellSize = int(math.sqrt(self.size))
        xStart = (x // cellSize)*cellSize
        yStart = (y // cellSize)*cellSize
        for row in range(yStart,yStart+cellSize):
            for col in range(xStart,xStart+cellSize):
                con.add(self.board[col][row].value)
        return con
    
    # for a given empty position on the board, identify constraints
    def findConstraints(self, x, y) -> set:
        constraints = set()
        # get row constraints
        constraints.update(self.rowConstraints(y))
        # get column constraints
        constraints.update(self.colConstraints(x))
        # get box constraints
        constraints.update(self.boxConstraints(x,y))
        return constraints
    
    # Initializes every variable on the board to its possible values based on constraints
    # This will minimize searching later
    def setDomains(self):
        for x in range(self.size):
            for y in range(self.size):
                con = self.findConstraints(x,y)
                # set the domain of variable
                if(self.board[x][y].value == 0):
                    self.board[x][y].domain = self.allValues.difference(con)
                # add the variable to the constraint array
                for c in con:
                    if(c > 0):
                        self.constraintArr[c-1].add(self.board[x][y])

    # remove val from domains in a row
    def updateRowConstraints(self, y, val):
        for x in range(len(self.board)):
            self.board[x][y].domain.discard(val)
            self.constraintArr[val-1].add(self.board[x][y])

    # remove val from domains in a col
    def updateColConstraints(self, x, val):
        for y in range(len(self.board[0])):
            self.board[x][y].domain.discard(val)
            self.constraintArr[val-1].add(self.board[x][y])

    # remove val from domains in a box
    def updateBoxConstraints(self, x, y, val):
        cellSize = int(math.sqrt(self.size))
        xStart = (x // cellSize)*cellSize
        yStart = (y // cellSize)*cellSize
        for row in range(yStart,yStart+cellSize):
            for col in range(xStart,xStart+cellSize):
                self.board[col][row].domain.discard(val)
                self.constraintArr[val-1].add(self.board[x][y])

    # assigns the variable in x, y to the value val
    def assignVariable(self, var, val):
        print("assigning ", val, "to ", var.position[0], var.position[1])
        var.value = val
        #update constraints for all affected variables
        self.updateRowConstraints(var.position[1], val)
        self.updateColConstraints(var.position[0], val)
        self.updateBoxConstraints(var.position[0], var.position[1], val)

    # searches the board for easy moves (where domain has 1 element)
    def searchOneElementDomains(self):
        keepGoing = True
        i = 0
        while keepGoing:
            keepGoing = False
            heapq.heapify(self.varHeap)
            # if the heap has a variable that has already been assigned, remove it
            while self.varHeap[0].value != 0:
                heapq.heappop(self.varHeap)
            # checks if the top variable of the heap can be resolved...
            while not self.checkIfSolved() and self.varHeap[0].value == 0 and len(self.varHeap[0].domain) == 1:
                val = self.varHeap[0].domain.pop()
                self.assignVariable(self.varHeap[0], val)
                heapq.heappop(self.varHeap)
                keepGoing = True
            self.printBoard()
            print("iteraton ", i)
            print("smallest domain ", self.varHeap[0].position, end=" {")
            for v in self.varHeap[0].domain:
                print(v, end=" ")
            print("}")
            i += 1
            input()

    def searchBoxRestrictions(self, val):
        cellSize = int(math.sqrt(self.size))
        # for every box on the board...
        for cellX in range(cellSize):
            for cellY in range(cellSize):
                available = []
                # add up all available variables for this value
                for x in range(cellX*cellSize, cellX*cellSize+cellSize):
                    for y in range(cellY*cellSize, cellY*cellSize+cellSize):
                        if self.board[x][y].value == 0 and self.board[x][y] not in self.constraintArr[val-1]:
                                available.append((x,y))
                # check if assignment can be made (only 1 available variable) 
                if len(available) == 1:
                    x,y = available[0]
                    self.assignVariable(self.board[x][y], val)
                    
    def searchRowRestrictions(self, val):
        for y in range(len(self.board[0])):
            available = []
            for x in range(len(self.board)):
                if self.board[x][y].value == 0 and self.board[x][y] not in self.constraintArr[val-1]:
                    available.append((x,y))
            # check if assignment can be made (only 1 available variable) 
            if len(available) == 1:
                x,y = available[0]
                self.assignVariable(self.board[x][y], val)

    def searchColRestrictions(self, val):
        for x in range(len(self.board)):
            available = []
            for y in range(len(self.board[0])):
                if self.board[x][y].value == 0 and self.board[x][y] not in self.constraintArr[val-1]:
                    available.append((x,y))
            # check if assignment can be made (only 1 available variable) 
            if len(available) == 1:
                x,y = available[0]
                self.assignVariable(self.board[x][y], val)
                    
    def searchAllRestrictions(self):
        for i in range(self.size):
            self.searchBoxRestrictions(i+1)
            self.searchRowRestrictions(i+1)
            self.searchColRestrictions(i+1)

    def printBoard(self):
        for x in range(self.size):
            print()
            for y in range(self.size):
                print(self.board[x][y].value, end=" ")

    def printConstraint(self, val):
         for x in range(self.size):
            print()
            for y in range(self.size):
                if self.board[x][y] in self.constraintArr[val-1]:
                    print("*", end=" ")
                else:
                    print("0", end=" ")

    def checkIfSolved(self):
        if len(self.varHeap) == 0:
            return True
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y].value == 0:
                    return False
        return True
        

    # algorithm for solving entire problem
    # right now it only searches for domains with 1 element
    # we will keep making this better...
    def solve(self):
        i = 0
        while not self.solved:
            print("SEARCH ONE ELEMENT DOMAINS")
            self.searchOneElementDomains()
            print("SEARCH RESTRICTIONS")
            self.searchAllRestrictions()
            self.solved = self.checkIfSolved()
            print("iteration ", i)
            i += 1
            self.printConstraint(9)
    
"------------------------------------------------------------------------------"

if __name__ == "__main__":
    # replace this later with code that reads from a file
    # I made the board a 9x9 for now to make visual testing easier
    board = [[0,0,0,0,0,0,2,0,0],
             [0,8,0,0,0,7,0,9,0],
             [6,0,2,0,0,0,5,0,0],
             [0,7,0,0,6,0,0,0,0],
             [0,0,0,9,0,1,0,0,0],
             [0,0,0,0,2,0,0,4,0],
             [0,0,5,0,0,0,6,0,3],
             [0,9,0,4,0,0,0,7,0],
             [0,0,6,0,0,0,0,0,0]
            ]
    solver = sudokuSolver(board, 9)
    solver.setDomains()
    solver.solve()
    solver.printBoard()
        
        
        
