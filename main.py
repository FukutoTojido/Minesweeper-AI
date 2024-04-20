from enum import Enum
from input import inputs

import random
import time

class NumberedSquare:
    def __init__(self, value, x, y):
        self.value = int(value)
        self.x = x
        self.y = y
    
    def getValue(self):
        return self.value

class SquareType(Enum):
    HIDDEN = 0
    MARKED = 1
    OPENED = 2

class BlankSquare:
    def __init__(self, value, x, y):
        if value == "■":
            self.type = SquareType.MARKED
        if value == "□":
            self.type = SquareType.OPENED

        self.x = x
        self.y = y

    def getValue(self):
        if self.type is SquareType.MARKED:
            return "■"
        if self.type is SquareType.OPENED:
            return "□"
    
    def mark(self):
        self.type = SquareType.MARKED
    
    def open(self):
        self.type = SquareType.OPENED

class Individual:
    def __init__(self, gene, fitness):
        self.gene = gene
        self.fitness = fitness

    def sort(generation):
        def key(indv):
            return indv.fitness
        
        generation.sort(key=key)

    def crossover(parent_1, parent_2):
        cut_off = random.randrange(0, len(parent_1))
        child_gene = parent_1[:cut_off] + parent_2[cut_off:]
        
        # mutate_rate = random.randint(0, 100)
        # if mutate_rate > 60:
        #     mutate_area = random.randrange(0, len(parent_1))
        #     child_gene = child_gene[:mutate_area] + ('0' if child_gene[mutate_area] == "1" else '1') + child_gene[mutate_area + 1:]

        # return child_gene
    
        result = ""
        for genome in child_gene:
            mutate_rate = random.randint(0, 100)

            if mutate_rate > 90:
                result += '0' if genome == "1" else "1"
                continue

            result += genome 

        return result

        # for idx, _ in enumerate(parent_1):
        #     probability = random.randint(0, 100)

        #     if probability < 35:
        #         child_gene += parent_1[idx]
        #         continue

        #     if probability < 70:
        #         child_gene += parent_2[idx]
        #         continue

        #     child_gene += random.choice(["0", "1"])

        # return child_gene

class Grid:
    def __init__(self, grid):
        self.grid = [[NumberedSquare(col[1], row[0], col[0]) if col[1] != "□" and col[1] != "■" else BlankSquare(col[1], row[0], col[0]) for col in enumerate(row[1])] for row in enumerate(grid)]
        self.num = []
        self.unknown = []

        for row in self.grid:
            for col in row:
                if isinstance(col, BlankSquare):
                    self.unknown.append(col)
                if isinstance(col, NumberedSquare):
                    self.num.append(col)

    def apply(self, gene):
        if len(gene) != len(self.unknown):
            return

        for idx, val in enumerate(gene):
            if val == "0":
                self.unknown[idx].open()
                continue

            self.unknown[idx].mark()

    def print(self):
        for row in self.grid:
            for col in row:
                print(col.getValue(), end = " ")
            print('\n')

    def getState(self):
        for square in self.unknown:
            if square.type == SquareType.MARKED:
                print("1", end = "")
            if square.type == SquareType.OPENED:
                print("0", end = "")

    def solve(self, verbose = False):
        if verbose:
            print("Start solving with Depth First Search")
        start_time = time.perf_counter()

        if (self.dfs(0, verbose) == 0):
            if verbose:
                print("Cannot find solution")
            return -1
        
        if verbose:
            print("Solution found!")
            self.print()

        end = time.perf_counter()
        length = end - start_time

        if verbose:
            print(f"""DFS took:\t{length} seconds""")

        return length

    def dfs(self, height, verbose = False):
        if height >= len(self.unknown): 
            eval = self.evaluate()
            if verbose:
                print("State:", end=" ")
                self.getState()
                print(f"\tEvaluation: {eval}")
            return eval
        
        self.grid[self.unknown[height].x][self.unknown[height].y].open()
        if (self.dfs(height + 1, verbose) == 1):
            return 1
        
        self.grid[self.unknown[height].x][self.unknown[height].y].mark()
        if (self.dfs(height + 1, verbose) == 1):
            return 1
        
        return 0
    
    def solve_genetics(self):
        pass
        
    def evaluate(self):
        for num in self.num:
            count = 0
            for i in [1, 0, -1]:
                for j in [1, 0, -1]:
                    if num.x + i < 0 or num.y + j < 0 or num.x + i >= len(self.grid) or num.y + j >= len(self.grid):
                        continue
                    if not isinstance(self.grid[num.x + i][num.y + j], BlankSquare):
                        continue
                    if self.grid[num.x + i][num.y + j].type == SquareType.MARKED:
                        count += 1

            # print(num.value, num.x, num.y, count, num.value == count)
            if count != num.value:
                return 0
            
        return 1

    def fitness(self):
        score = 0
        for num in self.num:
            count = 0
            for i in [1, 0, -1]:
                for j in [1, 0, -1]:
                    if num.x + i < 0 or num.y + j < 0 or num.x + i >= len(self.grid) or num.y + j >= len(self.grid):
                        continue
                    if not isinstance(self.grid[num.x + i][num.y + j], BlankSquare):
                        continue
                    if self.grid[num.x + i][num.y + j].type == SquareType.MARKED:
                        count += 1

            # print(num.value, num.x, num.y, count, num.value == count)
            score += abs(num.value - count)
            
        return score
    
    def genetic_algo(self, verbose = False):
        if verbose:
            print("Start solving with Genetics Algorithm")

        def create_gnome():
            str = ""
            for _ in self.unknown:
                str += random.choice(["0", "1"])

            self.apply(str)
            return Individual(str, self.fitness())

        start_time = time.perf_counter()

        generation = 0
        found = False
        
        POPULATION_SIZE = 200
        population = []

        for _ in range(POPULATION_SIZE):
            population.append(create_gnome())

        while not found:
            Individual.sort(population)
            if population[0].fitness <= 0:
                found = True
                self.apply(population[0].gene)
                break

            newGeneration = []
            for idx in range(round(POPULATION_SIZE * 0.05)):
                newGeneration.append(population[idx])

            for _ in range(round(POPULATION_SIZE * 0.95)):
                parent_1 = population[random.randrange(0, round(POPULATION_SIZE / 2))]
                parent_2 = population[random.randrange(0, round(POPULATION_SIZE / 2))]

                child_gene = Individual.crossover(parent_1.gene, parent_2.gene)
                self.apply(child_gene)
                newGeneration.append(Individual(child_gene, self.fitness()))

            population = newGeneration

            if verbose:
                print(f"""Generation: {generation}\tFitness: {population[0].fitness}""")
            
            # if population[0].fitness == 1:
            #     self.apply(population[0].gene)
            #     self.print()
            # print(f"""Generation: {generation}\tFitness: {[x.fitness for x in population]}""")
            generation += 1

        if verbose:
            print(f"""Generation: {generation}\tFitness: {population[0].fitness}""")
            self.print()

        end = time.perf_counter()
        length = end - start_time

        if verbose:
            print(f"""GA took:\t{length} second(s)""")

        return length


# grid = Grid([
#     ["□", "□", "1", "1", "□"],
#     ["□", "2", "□", "□", "□"],
#     ["2", "3", "□", "□", "□"],
#     ["□", "□", "2", "□", "1"],
#     ["□", "1", "1", "1", "1"]
# ])

# grid = Grid([
#     ["□", "□", "1", "1", "□"],
#     ["□", "1", "2", "2", "□"],
#     ["□", "□", "□", "□", "1"],
#     ["□", "2", "□", "□", "□"],
#     ["□", "□", "1", "□", "1"]
# ])

grid = Grid([
    ["1","2","□","□","□","2","1"],
    ["2","□","□","□","1","3","□"],
    ["2","□","□","1","□","□","□"],
    ["□","□","□","□","□","1","□"],
    ["□","2","2","□","3","□","□"],
    ["□","□","□","□","□","□","1"],
    ["□","1","□","0","□","□","□"]
])

# grid = Grid([
#     ["□","2","1","□","□","□","□","□","1","□"],
#     ["□","□","2","□","□","2","2","2","□","□"],
#     ["□","2","1","□","1","1","□","□","□","1"],
#     ["1","□","□","□","□","□","□","□","□","1"],
#     ["□","□","2","□","□","□","□","1","□","□"],
#     ["2","□","2","□","2","□","□","□","1","0"],
#     ["□","□","□","2","□","1","□","□","□","□"],
#     ["□","□","□","□","1","□","2","□","□","□"],
#     ["1","□","□","□","□","□","□","3","□","2"],
#     ["1","1","□","0","□","2","□","2","2","□"]
# ])

# grid = Grid([
#     ["2","□","2","0","□","□","□","□","□","□"],
#     ["□","□","□","□","□","□","2","□","□","1"],
#     ["2","□","□","□","2","□","□","□","2","□"],
#     ["□","3","□","□","2","□","□","□","2","1"],
#     ["1","□","□","5","□","□","1","□","□","1"],
#     ["□","□","□","□","3","2","□","□","□","□"],
#     ["1","□","4","□","4","2","□","□","□","0"],
#     ["□","2","□","□","□","2","□","3","□","□"],
#     ["□","□","4","□","□","□","□","□","□","1"],
#     ["□","1","2","2","2","□","□","3","□","□"]
# ])

# grid.print()

# grid.solve(verbose=True)
# grid.genetic_algo(verbose=True)

def benchmark():
    for type in ["5x5"]:
        perf_accm = 0
        dfs_accm = 0
        ga_accm = 0

        print(f'{"":<18s}{"DFS":<8s}{"GA":<8s}Performance')
        for idx, inp in enumerate(inputs[type]):
            grid = Grid(inp)
            dfs = grid.solve()
            ga = grid.genetic_algo()

            perf = dfs / ga - 1

            print(f"Problem #{idx + 1}\t{dfs:8.4f}{ga:8.4f}", end=" ")

            if perf == 0:
                print(perf)
            elif perf > 0:
                print("\033[92m {:.4f}%\033[00m" .format(perf * 100))
            elif perf < 0:
                print("\033[91m {:.4f}%\033[00m" .format(perf * 100))

            perf_accm += perf
            dfs_accm += dfs
            ga_accm += ga

        print(f"{type} benchmark:")
        print(f"└ DFS: {(dfs_accm / len(inputs[type])):.4f} seconds avg.")
        print(f"└ GA:  {(ga_accm / len(inputs[type])):.4f} seconds avg.")

        if perf_accm / len(inputs[type]) > 0:
            print(f"└ \033[92m {(perf_accm / len(inputs[type]) * 100):.4f}% \033[00m boost avg.")

        if perf_accm / len(inputs[type]) < 0:
            print(f"└ \033[91m {(perf_accm / len(inputs[type]) * 100):.4f}% \033[00m slowed down avg.")

benchmark()


# print(input.inputs["5x5"])
