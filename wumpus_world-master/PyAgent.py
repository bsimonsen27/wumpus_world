# PyAgent.py

import Action
import Orientation

# class created to represent each cell of the map
class Cell:
    def __init__(self):
        self.pit = False
        self.wumpus = False
        self.gold = False
        self.visited = False
        self.breeze = False
        self.stench = False

# class to help organize the wumpus world
class World:
    def __init__(self, size):
        self.size = size
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.agent_x = 0
        self.agent_y = 0

# function for interpreting percepts
def update_knowledge_from_percepts(world, x, y, breeze, stench):
    cell = world.grid[x][y]
    cell.visited = True
    cell.breeze = breeze
    cell.stench = stench

    if breeze:
        if x > 0:
            world.grid[x-1][y].pit = True  # Assuming the worst case; refine this later with more logic.
        if x < world.size - 1:
            world.grid[x+1][y].pit = True
        if y > 0:
            world.grid[x][y-1].pit = True
        if y < world.size - 1:
            world.grid[x][y+1].pit = True

    if stench:
        if x > 0:
            world.grid[x-1][y].wumpus = True
        if x < world.size - 1:
            world.grid[x+1][y].wumpus = True
        if y > 0:
            world.grid[x][y-1].wumpus = True
        if y < world.size - 1:
            world.grid[x][y+1].wumpus = True

# function for deciding safe locations
def infer_safe_locations(world):
    for x in range(world.size):
        for y in range(world.size):
            cell = world.grid[x][y]
            # A cell is safe if it has been visited or if it has no adjacent pits or Wumpus
            adjacent_safe = True
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < world.size and 0 <= ny < world.size:
                    if world.grid[nx][ny].pit or world.grid[nx][ny].wumpus:
                        adjacent_safe = False
            if cell.visited or (not cell.pit and not cell.wumpus and adjacent_safe):
                cell.safe = True

# function to hopefully choose a good next move
def choose_next_move(world):
    # Example strategy: find the closest safe, unvisited cell
    from collections import deque
    queue = deque([(world.agent_x, world.agent_y)])
    visited = set((world.agent_x, world.agent_y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.size and 0 <= ny < world.size and (nx, ny) not in visited:
                if world.grid[nx][ny].safe and not world.grid[nx][ny].visited:
                    return nx, ny
                visited.add((nx, ny))
                queue.append((nx, ny))
    return None  # No move found


def PyAgent_Constructor():
    """ PyAgent_Constructor: called at the start of a new trial """
    print("PyAgent_Constructor")


def PyAgent_Destructor():
    """ PyAgent_Destructor: called after all tries for a trial are complete """
    print("PyAgent_Destructor")


def PyAgent_Initialize():
    """ PyAgent_Initialize: called at the start of a new try """

    myworld = World(4)

    print("PyAgent_Initialize")


def PyAgent_Process(stench, breeze, glitter, bump, scream):
    """ PyAgent_Process: called with new percepts after each action to return the next action """

    percept_str = ""
    if stench == 1:
        percept_str += "Stench=True,"
    else:
        percept_str += "Stench=False,"
    if breeze == 1:
        percept_str += "Breeze=True,"
    else:
        percept_str += "Breeze=False,"
    if glitter == 1:
        percept_str += "Glitter=True,"
    else:
        percept_str += "Glitter=False,"
    if bump == 1:
        percept_str += "Bump=True,"
    else:
        percept_str += "Bump=False,"
    if scream == 1:
        percept_str += "Scream=True"
    else:
        percept_str += "Scream=False"
    
    print("PyAgent_Process: " + percept_str)

    return Action.GOFORWARD


def PyAgent_GameOver(score):
    """ PyAgent_GameOver: called at the end of each try """
    print("PyAgent_GameOver: score = " + str(score))
