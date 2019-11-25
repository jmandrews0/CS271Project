import time
import sudoku_solver
import loader


SIZE = 25
solver = sudoku_solver.sudokuSolver(loader.Loader(SIZE), SIZE)
solver.printBoard()
# start the clock
startTime = time.time()

solver.setDomains()
solver.solve()

# stop the clock
endTime = time.time() - startTime
solver.printBoard()
print("solved in", endTime, "seconds.")
