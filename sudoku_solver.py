# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 19:48:47 2019

@author: jmand
"""

# each cell in the board should contain a Variable
class Variable:
    # Domain for the variable
    domain = []
    # The value of the variable 0 means no assignment
    value = 0
    
    def __init__(self, value):
        self.value = value
    
class sudokuSolver:
    
    # The board will be a 2 dimensional array
    board = []
    # the 1 dimensional size of the board
    size = 0
    # a set of all possible values a variable could have
    allValues = set()
    
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
        return set()
    
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
    
    # arc consistency algorithm that runs over every cell of the board
    # we might not need this.....
    def AC3(self):
        pass
    
    # sub function for AC3
    def revise(self, Xi: Variable, Xj: Variable) -> bool:
        pass

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
        
        
        
