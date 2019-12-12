import math
import heapq
import loader
import verifier
#import time

# this constant says which number is consider to be no number set in this cell
EMPTY = 0

"------------------------------------------------------------------------------"
# each cell in the board should contain a Variable
class Variable:
    # Domain for the variable, current domain is the last or [-1] index
    domain = [set()]
    # The value of the variable EMPTY means no assignment
    value = EMPTY
    # The x and y axis location of this variable
    position = (0,0)
    
    def __init__(self, value, x, y):
        self.value = value
        self.position = (x,y)
        self.domain = [set()]
        self.heuristic = [0 for i in range(25)]

    def __lt__(self, other):
        return len(self.domain[-1]) < len(other.domain[-1])
    def __le__(self, other):
        return len(self.domain[-1]) <= len(other.domain[-1])
    def __eq__(self, other):
        return len(self.domain[-1]) == len(other.domain[-1])
    def __ne__(self, other):
        return len(self.domain[-1]) != len(other.domain[-1])
    def __gt__(self, other):
        return len(self.domain[-1]) > len(other.domain[-1])
    def __ge__(self, other):
        return len(self.domain[-1]) >= len(other.domain[-1])
    def __hash__(self):
        return self.position[0] + 25*self.position[1]
    def __str__(self):
        string = "cell (%d %d)"%(self.position[0], self.position[1])
        string += "{"
        for v in self.domain[-1]:
            string += str(v) + " "
        string += "}"
        return string

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
    # when searchmode is true, every assignment gets recorded, so the solver can backtrack
    searchMode = False
    # list of variables for backtracking
    backtrackList = []
    restoreSet = [set()]
    # boolean value identifying if the problem is solved yet
    solved = False
    # boolean value identifying if the problem has no solution
    error = False
    # size of a box cell
    cellSize = 5
    # how many of each value are present on board
    heuristic = []
    
    def __init__(self, board, size = 25):
        self.size = size
        self.searchDepth = 2
        self.cellSize = int(math.sqrt(self.size))
        self.allValues = set(i for i in range(1,size+1))
        #self.allValues = set(i for i in range(0,size))
        #print(self.allValues)
        # initialize constraintArr
        for i in range(size+1):
            self.constraintArr.append([set()])
        # initialize the board with Variable objects in each cell
        for x in range(size):
            self.board.append([])
            for y in range(size):
                self.board[-1].append(Variable(board[x][y],x,y))
                if self.board[-1][-1].value == EMPTY:
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
        xStart = (x // self.cellSize)*self.cellSize
        yStart = (y // self.cellSize)*self.cellSize
        for row in range(yStart,yStart+self.cellSize):
            for col in range(xStart,xStart+self.cellSize):
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
                if(self.board[x][y].value == EMPTY):
                    self.board[x][y].domain[-1] = self.allValues.difference(con)
                else:
                    self.constraintArr[0][-1].add(self.board[x][y])
                # add the variable to the constraint array
                if(self.board[x][y].value == EMPTY):
                    for c in self.allValues.difference(con):
                        self.constraintArr[c][-1].add(self.board[x][y])
                        
    #-----------------------------------------------------------------------------
    # Heuristic Least Constrained Value

    def countBoxConstraints(self, x, y, val):
        count = 0
        xStart = (x // self.cellSize)*self.cellSize
        yStart = (y // self.cellSize)*self.cellSize
        for row in range(yStart,yStart+self.cellSize):
            for col in range(xStart,xStart+self.cellSize):
                if val in self.board[col][row].domain[-1]:
                    count += 1
        return count
    
    def countRowConstraints(self, y, val):
        count = 0
        for x in range(len(self.board)):
            if val in self.board[x][y].domain[-1]:
                count += 1
        return count

    def countColConstraints(self, x, val):
        count = 0
        for y in range(len(self.board[0])):
            if val in self.board[x][y].domain[-1]:
                count += 1
        return count

    def countConstraints(self, var, val):
        x, y = var.position
        count = self.countBoxConstraints(x, y, val)
        count += self.countRowConstraints(y, val)
        count += self.countColConstraints(x, val)
        return count
    
    #-----------------------------------------------------------------------------
    
    # remove val from domains in a row
    def updateRowConstraints(self, y, val, skip=set()):
        for x in range(len(self.board)):
            if self.board[x][y] not in skip:
                self.board[x][y].domain[-1].discard(val)
                self.constraintArr[val][-1].discard(self.board[x][y])

    # remove val from domains in a col
    def updateColConstraints(self, x, val, skip=set()):
        for y in range(len(self.board[0])):
            if self.board[x][y] not in skip:
                self.board[x][y].domain[-1].discard(val)
                self.constraintArr[val][-1].discard(self.board[x][y])

    # remove val from domains in a box
    def updateBoxConstraints(self, x, y, val, skip=set()):
        xStart = (x // self.cellSize)*self.cellSize
        yStart = (y // self.cellSize)*self.cellSize
        for row in range(yStart,yStart+self.cellSize):
            for col in range(xStart,xStart+self.cellSize):
                if self.board[col][row] not in skip:
                    self.board[col][row].domain[-1].discard(val)
                    self.constraintArr[val][-1].discard(self.board[col][row])

    # assigns the variable in x, y to the value val
    def assignVariable(self, var, val, guess = False):
        #if guess:
        #    print("guess ", val, "to ", var.position[0], var.position[1])
        #else:
        #    print("assigning ", val, "to ", var.position[0], var.position[1])
        var.value = val
        var.domain[-1].discard(val)
        for i in range(1,self.size+1):
            self.constraintArr[i][-1].discard(var)
        self.constraintArr[0][-1].add(var)
        '''
        if not verifier.okSoFar(self):
            print("assigning ", val, "to ", var.position[0], var.position[1])
            print("not ok")
            self.printConstraint(val)
            print(var.domain[-1], "guessing: ", guess)
            raise Exception('invalid move')
            input()
        '''
        if guess:
            self.backtrackList.append(var)
            self.checkpointBoard()
            self.restoreSet[-1].add(var)
            
        elif self.searchMode:
            self.restoreSet[-1].add(var)
        #update constraints for all affected variables
        self.updateRowConstraints(var.position[1], val)
        self.updateColConstraints(var.position[0], val)
        self.updateBoxConstraints(var.position[0], var.position[1], val)
        self.error = self.checkIfError()
        

    def backTrack(self):
        #print("made a mistake, backtracking...")
        variable = self.backtrackList.pop()
        variable.heuristic[variable.value-1] -= 1
        #print(variable)
        #print(variable.heuristic)
        # restore board to last checkpoint
        self.restoreBoard()
        # reassign value
        if len(variable.domain[-1]) > 0:
            #val = variable.domain[-1].pop()
            values = iter(variable.domain[-1])
            bestVal = next(values)
            bestCount = self.countConstraints(variable, bestVal)
            for v in values:
                count = self.countConstraints(variable, v)
                if count < bestCount:
                    bestVal = v
                    bestCount = count
            #print(variable, "->", bestVal)
            variable.domain[-1].discard(bestVal)
            if len(variable.domain[-1]) == 0:
                self.assignVariable(variable, bestVal) # no longer a guess
            else:
                self.assignVariable(variable, bestVal, True) # still making a guess
        else:
            self.error = True
        # if there are no more guesses in the backtrack list, turn searchMode off
        if len(self.backtrackList) == 0:
            self.searchMode = False
        #variable.value = EMPTY
        # we don't know if this variable is in the queue or not, but it needs to be there
        # a duplicate variable in the varHeap should not be an issue, it will eventually get discarded
        self.varHeap.append(variable)
        #input()


    # restore the board to the last checkpoint
    def restoreBoard(self):
        for i in range(0,self.size+1):
            self.constraintArr[i].pop()
        for x in range(len(self.board)):
            for y in range(len(self.board[0])):
                self.board[x][y].domain.pop()
        for v in self.restoreSet[-1]:
            v.value = EMPTY;
            self.varHeap.append(v)
        self.restoreSet.pop()

    # create a restore point for the board when a guess is made
    def checkpointBoard(self):
        for i in range(0,self.size+1):
            self.constraintArr[i].append(set([v for v in self.constraintArr[i][-1]]))
        for x in range(len(self.board)):
            for y in range(len(self.board[0])):
                self.board[x][y].domain.append(set([v for v in self.board[x][y].domain[-1]]))
        self.restoreSet.append(set())

    #-----------------------------------------------------------------------------

    # searches the board for easy moves (where domain has 1 element)
    def searchOneElementDomains(self):
        assigned = False
        keepGoing = True
        i = 0
        while keepGoing:
            keepGoing = False
            heapq.heapify(self.varHeap)
            # if the heap has a variable that has already been assigned, remove it
            while len(self.varHeap) > 0 and self.varHeap[0].value != EMPTY:
                heapq.heappop(self.varHeap)
            # checks if the top variable of the heap can be resolved...
            while len(self.varHeap) > 0 and self.varHeap[0].value == EMPTY and len(self.varHeap[0].domain[-1]) == 1:
                val = self.varHeap[0].domain[-1].pop()
                var = heapq.heappop(self.varHeap)
                self.assignVariable(var, val)
                keepGoing = True
                assigned = True
            i += 1
        return assigned
            
    #-----------------------------------------------------------------------------

    def searchBoxRestrictions(self, val) -> bool:
        assigned = False
        available = [set() for i in range(self.size)]
        for var in self.constraintArr[val][-1]:
            if var.value == EMPTY:
                    cellX = var.position[0]//self.cellSize
                    cellY = var.position[1]//self.cellSize
                    key = cellX + cellY*self.cellSize
                    available[key].add(var)
        xWingBox = []
        for box in available:
            box1 = []
            for var in box:
                if val not in var.domain[-1]:
                    self.constraintArr[val][-1].discard(var)
                else:
                    box1.append(var)
            if len(box1) == 1:# and val in box[0].domain[-1]:
                self.assignVariable(box1[0], val)
                assigned = True
            elif len(box1) == 2:
                xWingBox.append(box1)
            
            # THIS IMPROVES SPEED
            if len(box1) > 1:
                # check if all in same row or col
                rowSame = True
                colSame = True
                row, col = box1[0].position
                for i in range(1, len(box1)):
                    if rowSame and row != box1[i].position[0]:
                        rowSame = False
                    if colSame and col != box1[i].position[1]:
                        colSame = False
                if rowSame:
                    # remove val from entire row
                    self.updateColConstraints(row, val, set(box1))
                if colSame:
                    # remove val from entire col
                    self.updateRowConstraints(col, val, set(box1))
            
        if len(xWingBox) == 2:
            self.searchXWing(xWingBox[0], xWingBox[1], val, False, False, True)
        return assigned
  
                    
    def searchRowRestrictions(self, val) -> bool:
        assigned = False
        available = [[] for i in range(self.size)]
        for var in self.constraintArr[val][-1]:
            if var.value == EMPTY:
                available[var.position[0]].append(var)
        xWingRows = []
        for row in available:
            row1 = []
            for var in row:
                if val not in var.domain[-1]:
                    self.constraintArr[val][-1].discard(var)
                else:
                    row1.append(var)
            if len(row1) == 1:# and val in row[0].domain[-1]:
                self.assignVariable(row1[0], val)
                assigned = True
            elif len(row1) == 2:
                xWingRows.append(row1)
            
            # THIS IMPROVES SPEED
            if len(row1) > 1:
                # check if all in same box
                cell = row1[0].position[0]//self.cellSize + self.cellSize*(row1[0].position[1]//self.cellSize)
                boxSame = True
                for i in range(1, len(row1)):
                    if boxSame and cell != row1[i].position[0]//self.cellSize + self.cellSize*(row1[i].position[1]//self.cellSize):
                        boxSame = False
                if boxSame:
                    # remove val from entire box
                    self.updateBoxConstraints(row1[0].position[0], row1[0].position[1], val, set(row1))
            
        if len(xWingRows) == 2:
            self.searchXWing(xWingRows[0], xWingRows[1], val, True, False, False)
        return assigned


    def searchColRestrictions(self, val) -> bool:
        assigned = False
        available = [[] for i in range(self.size)]
        for var in self.constraintArr[val][-1]:
            if var.value == EMPTY:
                available[var.position[0]].append(var)
        xWingCols = []
        for col in available:
            col1 = []
            for var in col:
                if val not in var.domain[-1]:
                    self.constraintArr[val][-1].discard(var)
                else:
                    col1.append(var)
            if len(col1) == 1:# and val in col[0].domain[-1]:
                self.assignVariable(col1[0], val)
                assigned = True
            elif len(col1) == 2:
                xWingCols.append(col1)
            
            # THIS IMPROVES SPEED
            if len(col1) > 1:
                # check if all in same box
                cell = col1[0].position[0]//self.cellSize + self.cellSize*(col1[0].position[1]//self.cellSize)
                boxSame = True
                for i in range(1, len(col1)):
                    if boxSame and cell != col1[i].position[0]//self.cellSize + self.cellSize*(col1[i].position[1]//self.cellSize):
                        boxSame = False
                if boxSame:
                    # remove val from entire box
                    self.updateBoxConstraints(col1[0].position[0], col1[0].position[1], val, set(col1))
            
        if len(xWingCols) == 2:
            self.searchXWing(xWingCols[0], xWingCols[1], val, False, True, False)
        return assigned

                    
    def searchAllRestrictions(self) -> bool:
        assigned = False
        for i in range(self.size):
            a = self.searchBoxRestrictions(i+1)
            if self.error:
                return True
            b = self.searchRowRestrictions(i+1)
            if self.error:
                return True
            c = self.searchColRestrictions(i+1)
            if self.error:
                return True
            if a or b or c:
                assigned = True
        return assigned
    
    #-----------------------------------------------------------------------------
    def searchXWing(self, group1, group2, val, isRow, isCol, isBox):
        # check for xwing pattern, are rows of points same
        if not isRow:
            if group1[0].position[1] == group2[0].position[1]:
                if group1[1].position[1] == group2[1].position[1]:
                    #print("found xwing in isRow", isRow, isCol, isBox)
                    #self.printConstraint(val)
                    self.updateRowConstraints(group1[0].position[1], val, set([group1[0], group2[0]]))
                    self.updateRowConstraints(group1[1].position[1], val, set([group1[1], group2[1]]))
                    #self.printConstraint(val)
                    #input()
            elif group1[0].position[1] == group2[1].position[1]:
                if group1[1].position[1] == group2[0].position[1]:
                    #print("found xwing in isRow", isRow, isCol, isBox)
                    #self.printConstraint(val)
                    self.updateRowConstraints(group1[0].position[1], val, set([group1[0], group2[1]]))
                    self.updateRowConstraints(group1[1].position[1], val, set([group1[1], group2[0]]))
                    #self.printConstraint(val)
                    #input()
        if not isCol:
            if group1[0].position[0] == group2[0].position[0]:
                if group1[1].position[0] == group2[1].position[0]:
                    #print("found xwing in isCol", isRow, isCol, isBox)
                    #self.printConstraint(val)
                    self.updateColConstraints(group1[0].position[0], val, set([group1[0], group2[0]]))
                    self.updateColConstraints(group1[1].position[0], val, set([group1[1], group2[1]]))
                    #self.printConstraint(val)
                    #input()
            elif group1[0].position[0] == group2[1].position[0]:
                if group1[1].position[0] == group2[0].position[0]:
                    #print("found xwing in isCol", isRow, isCol, isBox)
                    #self.printConstraint(val)
                    self.updateColConstraints(group1[0].position[0], val, set([group1[0], group2[1]]))
                    self.updateColConstraints(group1[1].position[0], val, set([group1[1], group2[0]]))
                    #self.printConstraint(val)
                    #input()
        if not isBox:
            # calculate box id's for each variable
            g1box1 = group1[0].position[0]//self.cellSize + self.cellSize*(group1[0].position[1]//self.cellSize)
            g1box2 = group1[1].position[0]//self.cellSize + self.cellSize*(group1[1].position[1]//self.cellSize)
            g2box1 = group2[0].position[0]//self.cellSize + self.cellSize*(group2[0].position[1]//self.cellSize)
            g2box2 = group2[1].position[0]//self.cellSize + self.cellSize*(group2[1].position[1]//self.cellSize)
            if g1box1 == g2box1:
                if g1box2 == g2box2:
                    #print("found xwing in isBox", isRow, isCol, isBox)
                    #self.printConstraint(val)
                    self.updateBoxConstraints(group1[0].position[0], group1[0].position[1], val, set([group1[0], group2[0]]))
                    self.updateBoxConstraints(group1[1].position[0], group1[1].position[1], val, set([group1[1], group2[1]]))
                    #self.printConstraint(val)
                    #input()
            if g1box1 == g2box2:
                if g1box2 == g2box1:
                    #print("found xwing in isBox", isRow, isCol, isBox)
                    #self.printConstraint(val)
                    self.updateBoxConstraints(group1[0].position[0], group1[0].position[1], val, set([group1[0], group2[1]]))
                    self.updateBoxConstraints(group1[1].position[0], group1[1].position[1], val, set([group1[1], group2[0]]))
                    #self.printConstraint(val)
                    #input()
    
    #-----------------------------------------------------------------------------

    # Make guesses when no other decisions can be made
    def makeVarGuess(self):
        heapq.heapify(self.varHeap)
        # make sure top value of heap is not already assigned
        if len(self.varHeap) == 0:
            return
        while self.varHeap[0].value != EMPTY:
            heapq.heappop(self.varHeap)
            heapq.heapify(self.varHeap)
        if len(self.varHeap[0].domain[-1]) == 0:
            error = True
            return
        # assign variable with smallest domain to a value, and record it in a stack
        #bestVal = self.varHeap[0].domain[-1].pop()
        
        values = iter(self.varHeap[0].domain[-1])
        bestVal = next(values)
        bestCount = self.countConstraints(self.varHeap[0], bestVal)
        for v in values:
            count = self.countConstraints(self.varHeap[0], v)
            if count < bestCount:
                bestVal = v
                bestCount = count
        #print(self.varHeap[0], "->", bestVal)
        self.varHeap[0].domain[-1].discard(bestVal)
        
        var = heapq.heappop(self.varHeap)
        if len(var.domain[-1]) > 0:
            self.assignVariable(var, bestVal, True)
        else:
            self.assignVariable(var, bestVal, False) # sometimes, not actually a guess
    
    #-----------------------------------------------------------------------------

    def printBoard(self):
        print()
        for x in range(self.size):
            print()
            for y in range(self.size):
                val = self.board[x][y].value if (self.board[x][y].value != EMPTY) else "*"
                print(val, end=" ")
                if (y+1) % int(math.sqrt(self.size)) == 0:
                    print("\t", end="")
            if (x+1) % int(math.sqrt(self.size)) == 0:
                print()

    def returnBoard(self):
         for x in range(self.size):
            for y in range(self.size):
                print(self.board[x][y].value-1, end="")

    def printConstraint(self, val):
        for x in range(self.size):
            print()
            for y in range(self.size):
                if self.board[x][y] in self.constraintArr[val][-1] and self.board[x][y] not in self.constraintArr[0][-1]:
                    print("0", end=" ")
                else:
                    print("*", end=" ")
        print()

    def checkIfSolved(self) -> bool:
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y].value == EMPTY:
                    return False
        return True

    def checkIfError(self) -> bool:
        heapq.heapify(self.varHeap)
        while len(self.varHeap) > 0 and self.varHeap[0].value != EMPTY:
            heapq.heappop(self.varHeap)
        if len(self.varHeap) == 0:
            return False
        #print("heap top: ", self.varHeap[0])
        #if len(self.varHeap[0].domain[-1]) == 0:
            #print("ERROR: ", self.varHeap[0])
        return len(self.varHeap[0].domain[-1]) == 0
        

    # algorithm for solving entire problem
    # right now it only searches for domains with 1 element
    # we will keep making this better...
    def solve(self):
        while not self.solved and not self.error:
            #print("-------------------- iteration ", i, " --------------------")
            #print("SEARCH ONE ELEMENT DOMAINS")
            self.searchOneElementDomains()
            #print("SEARCH RESTRICTIONS")
            assigned = self.searchAllRestrictions()
            # if nothing can be assigned, then backtrack search
            if not assigned:
                self.searchMode = True
            if self.searchMode and not assigned:
                #print("MAKE VARIABLE GUESS")
                self.makeVarGuess()
            
            # if backtrack mode is on, see if solution is consistent
            self.error = self.checkIfError()
            if self.searchMode:
                while self.error and len(self.backtrackList) > 0:
                    self.backTrack()
                    self.error = self.checkIfError()
                if len(self.backtrackList) == 0:
                    self.searchMode = False

            #if not verifier.okSoFar(self):
            #    print("not ok")
                
            self.solved = self.checkIfSolved()
            '''
            print("----------------------")
            for i,var in enumerate(self.backtrackList):
                off = len(self.backtrackList) - i
                string = "cell (%d %d)"%(var.position[0], var.position[1])
                string += "{"
                for v in var.domain[-1-off]:
                    string += str(v) + " "
                string += "}"
                print(string)
            self.printBoard()
            input()
            '''
            
        if self.solved:
            print("Solved!!")
            #correct = verifier.verify(self)
            #if not correct:
            #    raise Exception('wrong')
        if self.error:
            print("No solution!!")
    
"------------------------------------------------------------------------------"

if __name__ == "__main__":
    SIZE = 25
    solver = sudokuSolver(loader.Loader(SIZE), SIZE)
    solver.printBoard()
    solver.setDomains()
    solver.solve()
    solver.printBoard()
    '''
    solver.printConstraint(4)
    solver.searchRowRestrictions(4)
    solver.searchColRestrictions(4)
    solver.printConstraint(4)
    '''
