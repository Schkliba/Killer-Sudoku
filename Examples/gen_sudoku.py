"""
Author: František Dostál
"""
import sys
import random
import os

from dataclasses import InitVar, dataclass
from typing import Dict, List
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
    cage_sums: Dict
    base: int
    seed: int

    def __init__(self, base, board: List[List[int]], hints, seed) -> None:
        random.seed(seed)
        self.base = base
        self.generator_state = random.getstate()
        self.board = board
        self.cages = []
        self.mask = []
        self.cage_sums = {}
        self.gen_mask(hints)

    def gen_mask(self, n_missing: int):
        self.mask = []
        random.setstate(self.generator_state)
        for y in range(len(self.board)):
            current_row = []
            for x in range(len(self.board[y])):
                current_row.append(False)
            self.mask.append(current_row)

        
        for i in range(n_missing):
            y = random.randint(0,len(self.mask)-1)
            x = random.randint(0,len(self.mask[y])-1)
            while self.mask[y][x]:
                y = random.randint(0,len(self.mask)-1)
                x = random.randint(0,len(self.mask[y])-1)
            self.mask[y][x] = True
        
        self.generator_state = random.getstate()
    
    def neighbours(self,x,y):
        nlist = []
        if x-1 >= 0:
            nlist.append((x-1,y))    
        if x+1 < len(self.board):
            nlist.append((x+1,y))
        if y-1 >= 0:
            nlist.append((x,y-1))
        if y+1 < len(self.board):
            nlist.append((x,y+1))
        return nlist

    def gen_cages_invalid(self, n_cages):
        random.setstate(self.generator_state)
        self.cage_sums = {}
        for y in range(len(self.board)):
            current_row = []
            for x in range(len(self.board[y])):
                current_row.append(-1)
            self.cages.append(current_row)
        
        #starting configuration
        for i in range(n_cages):
            y = random.randint(0,len(self.cages)-1)
            x = random.randint(0,len(self.cages[y])-1)
            while self.cages[y][x] != -1:
                y = random.randint(0,len(self.cages)-1)
                x = random.randint(0,len(self.cages[y])-1)
            self.cages[y][x] = i
        
        #spreading cages
        carry_on = True
        while carry_on:
            carry_on = False
            for y in range(len(self.board)):
                for x in range(len(self.board[x])):
                    if self.cages[y][x] == -1:
                        carry_on = True  
                        hood = self.neighbours(x,y)
                        z = random.randint(0, len(hood)-1)
                        x_n, y_n = hood[z] 
                        if self.cages[y_n][x_n] > -1:    
                            self.cages[y][x] = self.cages[y_n][x_n]
                
        #generate solvable sums
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.cages[y][x] not in self.cage_sums:
                    self.cage_sums[self.cages[y][x]] = self.board[y][x]
                else:
                    self.cage_sums[self.cages[y][x]] += self.board[y][x]

        self.generator_state = random.getstate()

    def gen_cages_valid(self, n_cages):
        random.setstate(self.generator_state)
        self.cage_sums = {}
        for y in range(len(self.board)):
            current_row = []
            for x in range(len(self.board[y])):
                current_row.append(-1)
            self.cages.append(current_row)
        c_index = n_cages
        cage_sets = {}
        #starting configuration
        for i in range(n_cages):
            
            y = random.randint(0,len(self.cages)-1)
            x = random.randint(0,len(self.cages[y])-1)
            while self.cages[y][x] != -1:
                y = random.randint(0,len(self.cages)-1)
                x = random.randint(0,len(self.cages[y])-1)
            self.cages[y][x] = i
            cage_sets[i]=set([self.board[y][x]])
        
        #spreading cages
        carry_on = True
        while carry_on:
            carry_on = False
            for y in range(len(self.board)):
                for x in range(len(self.board[x])):
                    if self.cages[y][x] == -1:
                        carry_on = True  
                        hood = self.neighbours(x,y)
                        z = random.randint(0, len(hood)-1)
                        x_n, y_n = hood[z] 
                        if self.cages[y_n][x_n] > -1:
                            if self.board[y][x] not in cage_sets[self.cages[y_n][x_n]]:
                                self.cages[y][x] = self.cages[y_n][x_n]
                                cage_sets[self.cages[y_n][x_n]].add(self.board[y][x])
                            else:
                                #if the cage is invalid, split occurs
                                cage_sets[c_index]=set([self.board[y][x]])
                                self.cages[y][x] = c_index
                                c_index += 1
                
        #generate solvable sums
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.cages[y][x] not in self.cage_sums:
                    self.cage_sums[self.cages[y][x]] = self.board[y][x]
                else:
                    self.cage_sums[self.cages[y][x]] += self.board[y][x]

        self.generator_state = random.getstate()

    def getBoardString(self):
        lines = "["
        for y in range(len(self.board)):
            line = ""
            if y > 0:
                line += "             "
            line += "|"
            for x in range(len(self.board[y])):
                if self.mask[y][x]:
                    if x != 0:
                        line += ","
                    line += str(self.board[y][x])
                else:
                    if x != 0:
                        line += ","
                    line += str(0) 
            line += "\n"
            lines += line
        lines += "|]"
        return lines

    def getCageString(self):
        keys = sorted(list(self.cage_sums))
        line = "["
        for i in keys:
            if i > 0:
                line += ","
            line += str(self.cage_sums[i])
        line += "]"
        return line

    def getCageLayoutString(self):
        lines = "["
        for y in range(len(self.board)):
            lines += "\n"
            for x in range(len(self.board[y])):
                if x+y != 0:
                    lines += ","
                lines += str(self.cages[y][x]+1)
        lines += "]"
        return lines

    def __str__(self):
        output = "Base=" + str(self.base) + ";\n"
        output += "C=" + str(len(self.cage_sums)) + ";\n"
        output += "start_setup="+self.getBoardString()+";\n"
        output += "target_sum=" + self.getCageString()+";\n"
        output += "tile2cage=" + self.getCageLayoutString()+";\n"
        return output 


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

if __name__ == "__main__":
    SOLVABLE = False
    outputfile = "f-output4h35"#int(sys.argv[1])
    base = 4 #int(sys.argv[2])
    assert base > 0
    hints = 35
    # TODO: Seed not producing reliable results
    seed = 54 
    print("Starting Minizinc Module")

    gecode = Solver.lookup("gecode")
    model = Model()
    model.add_file(os.path.dirname(__file__) +"\\SudokuGeneration.mzn")
    model.output_type = Board
    instance = Instance(gecode, model)

    instance["Base"] = base

    result = instance.solve(verbose=True, debug_output=Path("./debug_output.txt"))
    kill_b:KillerSudokuBoard = result.solution.getKillerSudoku(base, hints, seed)

    print("Sudoku Generation Complete")
    print("Starting Cage Generation")
    if SOLVABLE:
        print("Valid")
        kill_b.gen_cages_valid(base*base*base)
    else: #Note: Sudokus obtained by the invalid process MAY be solvable, it's just not likely.
        print("Invalid")
        kill_b.gen_cages_invalid(base*base*base+2)

    with open(outputfile + '.dzn', 'w') as f:
        f.write(str(kill_b))
