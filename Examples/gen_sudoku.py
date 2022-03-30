import sys
import random

from dataclasses import InitVar, dataclass
from typing import List
from minizinc import Instance, Model, Solver
from pathlib import Path

class KillerSudokuCage:
    tuples: List

    def __init__(self, tuples) -> None:
        self.tuples = tuples
    
    def __add__(self, o):
        return KillerSudokuCage(self.tuples+o.tuples)

class KillerSudokuBoard:
    board: List[List[int]]
    mask: List[List[bool]]
    cages: List[List[int]]
    base: int
    seed: int

    def __init__(self, base, board: List[List[int]], hints, seed) -> None:
        random.seed(seed)
        self.base = base
        self.generator_state = random.getstate()
        self.board = board
        self.gen_mask(hints)

    def gen_mask(self, n_missing: int):
        self.mask = []
        random.setstate(self.generator_state)
        for y in range(len(self.board)):
            current_row = []
            for x in range(len(self.board[x])):
                current_row.append(False)
            self.mask.append(current_row)

        
        for i in range(n_missing):
            y = random.randint(len(self.mask))
            x = random.randint(len(self.mask[y]))
            while self.mask[y][x]:
                y = random.randint(len(self.mask))
                x = random.randint(len(self.mask[y]))
            self.mask[y][x] = True
        
        self.generator_state = random.getstate()

    def gen_cages(self):
        random.setstate(self.generator_state)
        for y in range(len(self.board)):
            current_row = []
            for x in range(len(self.board[x])):
                current_row.append(True)
            self.mask.append(current_row)

        self.generator_state = random.getstate()

@dataclass
class Board:
    board: List[List[int]]
    _output_item: InitVar[str] = None

    def __eq__(self, __o: object) -> bool:
        if len(__o.board) != len(self.board):
            return False
        for x in range(len(self.board)):
            for y in range(len(self.board)):
                if self.board[x][y] != __o.board[x][y]:
                    return False
        return True

    def getKillerSudoku(self, base, hints, seed):
        return KillerSudokuBoard(base, self.board,hints,seed)


base = int(sys.argv[1])
assert base > 0
n_solutions = int(sys.argv[2])
seed = int(sys.argv[3])


gecode = Solver.lookup("gecode")
model = Model()
model.add_file("SudokuGenration.mzn")
model.output_type = Board
instance = Instance(gecode, model)

instance["Base"] = base

result = instance.solve(verbose=True, debug_output=Path(
    "./debug_output.txt"), nr_solutions=n_solutions)
print(len(set(result.solution)))
print(set(result.solution))
