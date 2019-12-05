import math
import heapq
import KB
import loader
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
    # Knowledge Base
    kb = KB.KB()
    # boolean value identifying if the problem is solved yet
    solved = False
    # boolean value identifying if the problem has no solution
    error = False
    
    def __init__(self, board, size = 25):
        self.size = size
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
                if(self.board[x][y].value == EMPTY):
                    self.board[x][y].domain[-1] = self.allValues.difference(con)
                else:
                    self.constraintArr[0][-1].add(self.board[x][y])
                # add the variable to the constraint array
                for c in range(1,self.size+1):
                    if c not in con:
                        self.constraintArr[c][-1].add(self.board[x][y])
                        
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
    def updateBoxConstraints(self, x, y, val):
        cellSize = int(math.sqrt(self.size))
        xStart = (x // cellSize)*cellSize
        yStart = (y // cellSize)*cellSize
        for row in range(yStart,yStart+cellSize):
            for col in range(xStart,xStart+cellSize):
                self.board[col][row].domain[-1].discard(val)
                self.constraintArr[val][-1].discard(self.board[col][row])

    # assigns the variable in x, y to the value val
    def assignVariable(self, var, val, guess = False):
        #print("assigning ", val, "to ", var.position[0], var.position[1])
        var.value = val
        var.domain[-1].discard(val)
        if guess:
            self.backtrackList.append(var)
            self.checkpointBoard()
            self.restoreSet[-1].add(var)
        if self.searchMode:
            self.restoreSet[-1].add(var)
        #update constraints for all affected variables
        self.updateRowConstraints(var.position[1], val)
        self.updateColConstraints(var.position[0], val)
        self.updateBoxConstraints(var.position[0], var.position[1], val)
        self.error = self.checkIfError()
        

    def backTrack(self):
        #print("made a mistake, backtracking...")
        variable = self.backtrackList.pop()
        # restore board to last checkpoint
        self.restoreBoard()
        # reassign value
        if len(variable.domain[-1]) > 0:
            val = variable.domain[-1].pop()
            if len(variable.domain[-1]) == 0:
                self.assignVariable(variable, val) # no longer a guess
            else:
                self.assignVariable(variable, val, True) # still making a guess
        else:
            #print("NO SOLUTION")
            self.error = True
        # if there are no more guesses in the backtrack list, turn searchMode off
        if len(self.backtrackList) == 0:
            self.searchMode = False
        #variable.value = EMPTY
        # we don't know if this variable is in the queue or not, but it needs to be there
        # a duplicate variable in the varHeap should not be an issue, it will eventually get discarded
        self.varHeap.append(variable)

    # restore the board to the last checkpoint
    def restoreBoard(self):
        for i in range(self.size+1):
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
        for i in range(self.size+1):
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
        cellSize = int(math.sqrt(self.size))
        available = [[] for i in range(self.size)]
        for var in self.constraintArr[val][-1]:
            if var.value == EMPTY:
                cellX = var.position[0]//cellSize
                cellY = var.position[1]//cellSize
                key = cellX + cellY*cellSize
                available[key].append(var)
        for box in available:
            if len(box) == 1:
                self.assignVariable(box[0], val)
                assigned = True
            # THIS IMPROVES SPEED
            elif len(box) > 1:
                # check if all in same row or col
                rowSame = True
                colSame = True
                row, col = box[0].position
                for i in range(1, len(box)):
                    if rowSame and row != box[i].position[0]:
                        rowSame = False
                    if colSame and col != box[i].position[1]:
                        colSame = False
                if rowSame:
                    # remove val from entire row
                    self.updateColConstraints(row, val, set(box))
                if colSame:
                    # remove val from entire col
                    self.updateRowConstraints(col, val, set(box))
        return assigned
        '''
        assigned = False
        cellSize = int(math.sqrt(self.size))
        # for every box on the board...
        for cellX in range(cellSize):
            for cellY in range(cellSize):
                available = []
                # add up all available variables for this value
                for x in range(cellX*cellSize, cellX*cellSize+cellSize):
                    for y in range(cellY*cellSize, cellY*cellSize+cellSize):
                        if self.board[x][y].value == EMPTY and self.board[x][y] in self.constraintArr[val][-1]:
                                available.append((x,y))
                # check if assignment can be made (only 1 available variable) 
                if len(available) == 1:
                    x,y = available[0]
                    self.assignVariable(self.board[x][y], val)
                    assigned = True
                    if self.error:
                        return True
                # THIS IMPROVES SPEED
                elif len(available) > 1:
                    # check if all in same row or col
                    rowSame = True
                    colSame = True
                    row, col = available[0]
                    for i in range(1, len(available)):
                        if rowSame and row != available[i][0]:
                            rowSame = False
                        if colSame and col != available[i][1]:
                            colSame = False
                    if rowSame:
                        # remove val from entire row
                        self.updateColConstraints(row, val, set(available))
                    if colSame:
                        # remove val from entire col
                        self.updateRowConstraints(col, val, set(available))
        return assigned
        '''
                    
    def searchRowRestrictions(self, val) -> bool:
        assigned = False
        available = [[] for i in range(self.size)]
        for var in self.constraintArr[val][-1]:
            if var.value == EMPTY:
                available[var.position[1]].append(var)
        for row in available:
            if len(row) == 1:
                self.assignVariable(row[0], val)
                assigned = True
        return assigned
        '''
        assigned = False
        for y in range(len(self.board[0])):
            available = []
            for x in range(len(self.board)):
                if self.board[x][y].value == EMPTY and self.board[x][y] in self.constraintArr[val][-1]:
                    available.append((x,y))
            # check if assignment can be made (only 1 available variable) 
            if len(available) == 1:
                x,y = available[0]
                self.assignVariable(self.board[x][y], val)
                if self.error:
                    return True
                assigned = True
        return assigned
        '''

    def searchColRestrictions(self, val) -> bool:
        assigned = False
        available = [[] for i in range(self.size)]
        for var in self.constraintArr[val][-1]:
            if var.value == EMPTY:
                available[var.position[0]].append(var)
        for col in available:
            if len(col) == 1:
                self.assignVariable(col[0], val)
                assigned = True
        return assigned
        '''
        assigned = False
        for x in range(len(self.board)):
            available = []
            for y in range(len(self.board[0])):
                if self.board[x][y].value == EMPTY and self.board[x][y] in self.constraintArr[val][-1]:
                    available.append((x,y))
            # check if assignment can be made (only 1 available variable) 
            if len(available) == 1:
                x,y = available[0]
                self.assignVariable(self.board[x][y], val)
                if self.error:
                    return True
                assigned = True
        return assigned
        '''
                    
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
    # THIS IS SLOW AND NOT USEFULL -----------------------------------------------
    
    def tellKB(self, terms, val):
        pclause = set()
        for t in terms:
            pclause.add( KB.Term("c%d%d=%d"%(t[0], t[1], val)) )
        pClause = KB.Clause(pclause)
        self.kb.tell(pClause)
        
        for t1 in terms:
            for t2 in terms:
                if t1 != t2:
                    term1 = KB.Term("c%d%d=%d"%(t1[0], t1[1], val),True)
                    term2 = KB.Term("c%d%d=%d"%(t2[0], t2[1], val),True)
                    nClause = KB.Clause([term1,term2])
                    self.kb.tell(nClause)
        print("KB size: ", len(self.kb.kb))

    def askKB(self, var, val):
        name = "c%d%d=%d"%(var.position[0], var.position[1], val)
        return self.kb.ask(KB.Clause([KB.Term(name)]))
        
        
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
        #if len(self.varHeap) > 0:
        #    print("smallest domain ", self.varHeap[0])
        val = self.varHeap[0].domain[-1].pop()
        var = heapq.heappop(self.varHeap)
        self.assignVariable(var, val, True)
    
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
        #print()

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
        return len(self.varHeap[0].domain[-1]) == 0
        

    # algorithm for solving entire problem
    # right now it only searches for domains with 1 element
    # we will keep making this better...
    def solve(self):
        i = 0
        while not self.solved and not self.error:
            #print("-------------------- iteration ", i, " --------------------")
            #print("SEARCH ONE ELEMENT DOMAINS")
            self.searchOneElementDomains()
            #print("SEARCH RESTRICTIONS")
            assigned = self.searchAllRestrictions()
            #print("assigned: ", assigned)
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
                
            self.solved = self.checkIfSolved()
            i += 1
            #self.printBoard()
            #input()
            
        if self.solved:
            print("Solved!!")
        if self.error:
            print("No solution!!")
    
"------------------------------------------------------------------------------"

if __name__ == "__main__":
    SIZE = 16
    solver = sudokuSolver(loader.Loader(SIZE), SIZE)
    solver.printBoard()
    solver.setDomains()
    solver.solve()
    solver.printBoard()
