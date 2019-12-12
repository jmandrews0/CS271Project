import sudoku_solver
import math

def verify(solver) -> bool:
    # check rows
    for x in range(len(solver.board)):
        numbers = set([i for i in range(1,solver.size+1)])
        for y in range(len(solver.board[0])):
            numbers.discard(solver.board[x][y].value)
        if len(numbers) > 0:
            print(x,y, numbers)
            return False
    # check columns
    for y in range(len(solver.board[0])):
        numbers = set([i for i in range(1,solver.size+1)])
        for x in range(len(solver.board)):
            numbers.discard(solver.board[x][y].value)
        if len(numbers) > 0:
            print(x, y, numbers)
            return False
    # check boxes
    cellSize = int(math.sqrt(solver.size))
    for cellX in range(cellSize):
        for cellY in range(cellSize):
            numbers = set([i for i in range(1,solver.size+1)])
            # add up all available variables for this value
            for x in range(cellX*cellSize, cellX*cellSize+cellSize):
                for y in range(cellY*cellSize, cellY*cellSize+cellSize):
                    numbers.discard(solver.board[x][y].value)
            if len(numbers) > 0:
                print(x, y, numbers)
                return False
    # if everything was fine...
    return True


def okSoFar(solver) -> bool:
    # check rows
    for x in range(len(solver.board)):
        numbers = [0 for i in range(0,solver.size+1)]
        for y in range(0,len(solver.board[0])):
            numbers[solver.board[x][y].value] += 1
            if numbers[solver.board[x][y].value] > 1 and solver.board[x][y].value != 0:
                solver.printBoard()
                print("row", x,y, solver.board[x][y].value)
                return False
    # check columns
    for y in range(len(solver.board[0])):
        numbers = [0 for i in range(0,solver.size+1)]
        for x in range(0,len(solver.board)):
            numbers[solver.board[x][y].value] += 1
            if numbers[solver.board[x][y].value] > 1 and solver.board[x][y].value != 0:
                print("col", x,y, solver.board[x][y].value)
                return False
    # check boxes
    cellSize = int(math.sqrt(solver.size))
    for cellX in range(cellSize):
        for cellY in range(cellSize):
            numbers = [0 for i in range(0,solver.size+1)]
            # add up all available variables for this value
            for x in range(cellX*cellSize, cellX*cellSize+cellSize):
                for y in range(cellY*cellSize, cellY*cellSize+cellSize):
                    numbers[solver.board[x][y].value] += 1
                    if numbers[solver.board[x][y].value] > 1 and solver.board[x][y].value != 0:
                        print("box", x,y, solver.board[x][y].value)
                        return False
    # if everything was fine...
    return True
