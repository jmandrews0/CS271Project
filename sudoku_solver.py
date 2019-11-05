import math

"------------------------------------------------------------------------------"
# each cell in the board should contain a Variable
class Variable:
    # Domain for the variable
    domain = set()
    # The value of the variable 0 means no assignment
    value = 0
    
    def __init__(self, value):
        self.value = value

"------------------------------------------------------------------------------"
class sudokuSolver:
    
    # The board will be a 2 dimensional array
    board = []
    # the 1 dimensional size of the board
    size = 0
    # a set of all possible values a variable could have
    allValues = set()
    # boolean value identifying if the problem is solved yet
    solved = False
    
    def __init__(self, board, size = 25):
        self.size = size
        self.allValues = set(i for i in range(1,size+1))
        # initialize the board with Variable objects in each cell
        for x in range(size):
            self.board.append([])
            for y in range(size):
                self.board[-1].append(Variable(board[x][y]))
    
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
                if(self.board[x][y].value == 0):
                    self.board[x][y].domain = self.allValues.difference(con)

    # remove val from domains in a row
    def updateRowConstraints(self, y, val):
        for x in range(len(self.board)):
            self.board[x][y].domain.discard(val)

    # remove val from domains in a col
    def updateColConstraints(self, x, val):
        for y in range(len(self.board[0])):
            self.board[x][y].domain.discard(val)

    # remove val from domains in a box
    def updateBoxConstraints(self, x, y, val):
        cellSize = int(math.sqrt(self.size))
        xStart = (x // cellSize)*cellSize
        yStart = (y // cellSize)*cellSize
        for row in range(yStart,yStart+cellSize):
            for col in range(xStart,xStart+cellSize):
                self.board[col][row].domain.discard(val)

    # assigns the variable in x, y to the value val
    def assignVariable(self, x, y, val):
        self.board[x][y].value = val
        #update constraints for all affected variables
        self.updateRowConstraints(y, val)
        self.updateColConstraints(x, val)
        self.updateBoxConstraints(x, y, val)

    # searches the board for easy moves (where domain has 1 element)
    def searchOneElementDomains(self):
        for x in range(self.size):
            for y in range(self.size):
                if len(self.board[x][y].domain) == 1:
                        #print(self.board[x][y].domain)
                        val = self.board[x][y].domain.pop()
                        self.assignVariable(x,y,val)
                        #self.printBoard()
                        #print("added ", val, "to ", x, y)
                        #input()

    def printBoard(self):
        for x in range(self.size):
            print()
            for y in range(self.size):
                print(self.board[x][y].value, end=" ")

    def checkIfSolved(self):
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
            self.searchOneElementDomains()
            self.solved = self.checkIfSolved()
            print("iteration ", i)
            i += 1
    
"------------------------------------------------------------------------------"

if __name__ == "__main__":
    # replace this later with code that reads from a file
    # I made the board a 9x9 for now to make visual testing easier
    board = [[0,2,0,9,0,0,0,0,0],
             [8,0,7,5,0,1,0,0,0],
             [0,0,5,0,0,0,3,0,6],
             [0,9,2,0,0,0,0,0,0],
             [7,0,0,0,8,0,0,6,0],
             [1,0,0,0,4,0,0,2,9],
             [0,0,0,0,0,2,7,4,5],
             [0,4,0,0,3,6,0,0,0],
             [0,0,9,1,0,0,0,0,3]
            ]
    solver = sudokuSolver(board, 9)
    solver.setDomains()
    solver.solve()
    solver.printBoard()
        
        
        
