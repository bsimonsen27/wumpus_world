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
        self.safe = False
        self.pit_probability = 0.0          # keep track of a cell's pit probability
        self.wumpus_probability = 0.0       # track probability of wumpus
        

# class to help organize the wumpus world
# initial values of events declared
class World:
    def __init__(self, size):
        # size is given from Wumpsim.py, should be 4x4 for this assignment
        self.size = size
        # create a grid where each cell if of the Cell class declared above
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        # will be 0 indexing. Agent begins in bottom left cell
        self.agent_x = 0
        self.agent_y = 0
        # from Wumpsim.py, Agent begins by facing to the right 
        self.agent_orientation = Orientation.RIGHT
        self.agent_has_gold = False
        self.agent_has_arrow = True
        self.wumpus_alive = True
        

# function for interpreting percepts and updating the Agent's knowledge of the cave
def update_knowledge_from_percepts(world, x, y, breeze, stench):
    cell = world.grid[x][y]
    cell.visited = True
    cell.breeze = breeze
    cell.stench = stench

    # update possible pit locations based on if breeze percept == True
    if breeze:
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.size and 0 <= ny < world.size:
                if not world.grid[nx][ny].visited and not world.grid[nx][ny].safe:
                    world.grid[nx][ny].pit = True

    # update possible wumpus locations based on if stench percept == True                 
    if stench and world.wumpus_alive:
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.size and 0 <= ny < world.size:
                if not world.grid[nx][ny].visited and not world.grid[nx][ny].safe:
                    world.grid[nx][ny].wumpus = True

    # no dangerous percepts for pit or wumpus were True                
    if not breeze and (not stench or not world.wumpus_alive):
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.size and 0 <= ny < world.size:
                world.grid[nx][ny].safe = True
                world.grid[nx][ny].wumpus_probability = 0.
                world.grid[nx][ny].pit_probability = 0.
                
    if world.grid[x][y].visited:
        world.grid[x][y].safe = True

# function to hopefully choose a good next move
def choose_next_move(world):
    # Example strategy: find the closest safe, unvisited cell
    from collections import deque
    # use a deque to iterate through possible steps
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
    return None

# helper function to determine the orientation of the target relative to the agent
def get_target_orientation(world, target_x, target_y):
    agent_x, agent_y = world.agent_x, world.agent_y
    if target_x < agent_x:
        target_orientation = Orientation.DOWN
    elif target_x > agent_x:
        target_orientation = Orientation.UP
    elif target_y > agent_y:
        target_orientation = Orientation.RIGHT
    else:
        target_orientation = Orientation.LEFT
    return target_orientation

# function to determine which way the agent needs to turn to be facing in the target direction
# go_forward is a global variable to insure the agent takes the safe route when facing the right direction
go_forward = False
def determine_turn(world, target_x, target_y):
    global go_forward
    agent_x, agent_y = world.agent_x, world.agent_y
    orientation = world.agent_orientation

    target_orientation = get_target_orientation(world, target_x, target_y)

    # Check if the direct path to the target is safe
    if (target_orientation == Orientation.DOWN and world.grid[agent_x - 1][agent_y].safe) or \
       (target_orientation == Orientation.UP and world.grid[agent_x + 1][agent_y].safe) or \
       (target_orientation == Orientation.RIGHT and world.grid[agent_x][agent_y + 1].safe) or \
       (target_orientation == Orientation.LEFT and world.grid[agent_x][agent_y - 1].safe):
        # If the direct path is safe, turn directly to the target
        if orientation == target_orientation:
            return None
        elif (orientation + 1) % 4 == target_orientation:
            world.agent_orientation = target_orientation
            return Action.TURNLEFT
        else:
            world.agent_orientation = (orientation - 1) % 4
            return Action.TURNRIGHT
    # if the direct path is not safe choose a safe path perpendicular to the direct path using recursion
    else:
        if target_orientation == Orientation.DOWN or target_orientation == Orientation.UP:
            for dy in [-1, 1]:
                ny = agent_y + dy
                if 0 <= ny < world.size:
                    if world.grid[agent_x][ny].safe:
                        if get_target_orientation(world, agent_x, ny) != (orientation + 2) % 4:
                            go_forward = True
                        return determine_turn(world, agent_x, ny)
        elif target_orientation == Orientation.LEFT or target_orientation == Orientation.RIGHT:
            for dx in [-1, 1]:
                nx = agent_x + dx
                if 0 <= nx < world.size:
                    if world.grid[nx][agent_y].safe:
                        if get_target_orientation(world, nx, agent_y) != (orientation + 2) % 4:
                            go_forward = True
                        return determine_turn(world,nx,agent_y)
                    
                    
# function to adjust the agents x,y position on movement
def adjust_coordinates(world):
    global start
    start = False
    orientation = world.agent_orientation
    if orientation == Orientation.RIGHT and world.agent_y < world.size:
        world.agent_y += 1
    elif orientation == Orientation.LEFT and world.agent_y > 0:
        world.agent_y -= 1
    elif orientation == Orientation.UP and world.agent_x < world.size:
        world.agent_x += 1
    elif world.agent_x > 0:
        world.agent_x -= 1
    else:
        return
    
# function for determing pit probability
# should only be called if breeze is true
def pit_probability(world):
    x = world.agent_x
    y = world.agent_y
    
    unsafe_neighbors = []
    
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < world.size and 0 <= ny < world.size:
            if not world.grid[nx][ny].safe:
                unsafe_neighbors.append((nx, ny))
    
    if len(unsafe_neighbors) == 1:
        nx, ny = unsafe_neighbors[0]
        world.grid[nx][ny].pit_probability = 1.0
    else:
        for nx, ny in unsafe_neighbors:
            world.grid[nx][ny].pit_probability += 0.1
    
    return


# determine the wumpus probability
# called if stench == True
def wumpus_probability(world):
    x = world.agent_x
    y = world.agent_y
    
    unsafe_neighbors = []
    
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < world.size and 0 <= ny < world.size:
            if not world.grid[nx][ny].safe:
                unsafe_neighbors.append((nx, ny))
    # If only one unsafe neighbor is found it must be the wumpus
    if len(unsafe_neighbors) == 1:
        for x1 in range(world.size):
            for y1 in range(world.size):
                # sets all cells that had a probability of being a wumpus to safe except the confirmed cell and suspected pits
                if world.grid[x1][y1].wumpus_probability > 0 and world.grid[x1][y1].pit_probability == 0.:
                    world.grid[x1][y1].safe = True
                world.grid[x1][y1].wumpus_probability = 0.
        nx, ny = unsafe_neighbors[0]
        world.grid[nx][ny].wumpus_probability = 1.0
        world.grid[nx][ny].safe = False
    else:
        for nx, ny in unsafe_neighbors:
            if world.grid[nx][ny].wumpus_probability >= 0.2:
                for x1 in range(world.size):
                    for y1 in range(world.size):
                        # sets all cells that had a probability of being a wumpus to safe except the confirmed cell and suspected pits
                        if world.grid[x1][y1].wumpus_probability > 0 and world.grid[x1][y1].pit_probability == 0.:
                            world.grid[x1][y1].safe = True
                        world.grid[x1][y1].wumpus_probability = 0.
                world.grid[nx][ny].wumpus_probability = 1.0
                world.grid[nx][ny].safe = False
                break
            else:
                world.grid[nx][ny].wumpus_probability += 0.1
    
    return

# print the pit probability of all the cells
def print_pit_probability(world):
    print("\nPrinting pit probability for each cell:")
    for x in range(world.size):
        #print("")
        for y in range(world.size):
            # print the pit probability of every cell
            if world.grid[x][y].safe == True:
                world.grid[x][y].pit_probability = 0.0
                world.grid[x][y].wumpus_probability = 0.0
            print(f"|Cell[{x}][{y}] pit_prob:{world.grid[x][y].pit_probability} wumpus_prob:{world.grid[x][y].wumpus_probability}|safety:{world.grid[x][y].safe}")
        print("") 
    print("")
    return

# debug function to show current world state
def world_state(world):
    for x in range(world.size):
        for y in range(world.size):  
            print(f"x:{x}, y:{y}, \t safe:{world.grid[x][y].safe} \t visited:{world.grid[x][y].visited}"
                  f"\tpit:{world.grid[x][y].pit} \t wumpus:{world.grid[x][y].wumpus}\
                  breeze:{world.grid[x][y].breeze} \t stench:{world.grid[x][y].stench}\n")

def get_frontier(world):
    frontier= []
    for x in range(world.size):
        for y in range(world.size):
            if world.grid[x][y].visited:
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    nx, ny = x + dx, y + dy
                    if nx >= 0 and nx < world.size and ny >= 0 and ny < world.size and not world.grid[nx][ny].visited:
                        frontier.append((nx,ny))
    return frontier

    

def PyAgent_Constructor():
    """ PyAgent_Constructor: called at the start of a new trial """
    print("PyAgent_Constructor")


def PyAgent_Destructor():
    """ PyAgent_Destructor: called after all tries for a trial are complete """
    print("PyAgent_Destructor")


def PyAgent_Initialize():
    """ PyAgent_Initialize: called at the start of a new try """
    global myworld
    myworld = World(4)

    print("PyAgent_Initialize")
    
# start tells us that we haven't left the start pos 0, 0 yet
start = True
# shot is on for one round immediately after the arrow is shot to insure the agent moves forward
# when the Wumpus is not shot
shot = False

def PyAgent_Process(stench, breeze, glitter, bump, scream):
    """ PyAgent_Process: called with new percepts after each action to return the next action """
    global myworld, go_forward, start, shot
    
    # position correction for if the cell value somehow exceeds the world size
    if myworld.agent_x >= myworld.size:
        myworld.agent_x = myworld.size - 1
    if myworld.agent_y >= myworld.size:
        myworld.agent_y = myworld.size - 1
    
    # only update the pit_probabilities if there is a breeze and agent hasn't visited cell
    if breeze and myworld.grid[myworld.agent_x][myworld.agent_y].visited == False:
        pit_probability(myworld)
        
    # only update if in a new cell and wumpus is still alive
    if stench and myworld.grid[myworld.agent_x][myworld.agent_y].visited == False and myworld.wumpus_alive == True:
        wumpus_probability(myworld)
    # if wumpus is killed, wumpus_probability will be 0.0
    if shot and not myworld.wumpus_alive:
        for x in range(myworld.size):
            for y in range(myworld.size):
                myworld.grid[x][y].wumpus_probability = 0.0 


    # Update world knowledge with new percepts
    update_knowledge_from_percepts(myworld, myworld.agent_x, myworld.agent_y, breeze, stench)
        
    #world_state(myworld)
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

    print_pit_probability(myworld)
    
    if glitter == 1:
        myworld.agent_has_gold = True 
        return Action.GRAB
     
    # if there is a stench and the agent isn't facing a 'wall' shoot, this will result
    # in either killing the Wumpus, or tells us that the wumpus isn't in front of us
    if stench:
        if myworld.agent_has_arrow and \
           not (myworld.agent_orientation == Orientation.RIGHT and myworld.agent_y + 1 >= myworld.size) and\
           not (myworld.agent_orientation == Orientation.UP and myworld.agent_x + 1 >= myworld.size) and\
           not (myworld.agent_orientation == Orientation.LEFT and myworld.agent_y - 1 < 0) and\
           not (myworld.agent_orientation == Orientation.DOWN and myworld.agent_x - 1 < 0):
            myworld.agent_has_arrow = False
            shot = True
            return Action.SHOOT
        elif scream:
            myworld.wumpus_alive = False
            update_knowledge_from_percepts(myworld, myworld.agent_x, myworld.agent_y, breeze, stench)
            adjust_coordinates(myworld)
            if not breeze:
                return Action.GOFORWARD
        elif shot and not breeze:
            shot = False
            # Increase wumpus probability since the wumpus wasn't shot we are more sure of where it is
            wumpus_probability(myworld)
            adjust_coordinates(myworld)
            return Action.GOFORWARD
    
    # Get the next move from the path
    if not myworld.agent_has_gold:
        next_move = choose_next_move(myworld)
        # better logic is needed, currently if we are at 0,0 and there is a pit next to us retreat
        if next_move is None:
            if start:
                return Action.CLIMB
            # if no more safe moves are found use probability to find next safest move
            else:
                nx = 0
                ny = 0
                best_prob = 1
                frontiers = get_frontier(myworld)
                print(f"Frontier: {frontiers}")
                
                # Count the occurrences of each (x, y) pair
                frontier_counts = {}
                for x, y in frontiers:
                    if (x, y) not in frontier_counts:
                        frontier_counts[(x, y)] = 0
                    frontier_counts[(x, y)] += 1
                
                for (x, y), count in frontier_counts.items():
                    prob = myworld.grid[x][y].pit_probability + myworld.grid[x][y].wumpus_probability
                    if (count == 2 and prob < 0.2) or (count == 3 and prob < 0.3):
                        best_prob = prob
                        nx = x
                        ny = y
                        break
                    elif prob < best_prob:
                        best_prob = prob
                        nx = x
                        ny = y
                # Assume the chosen frontier is safe to allow other logic to move to target cell
                myworld.grid[nx][ny].safe = True
                print(f"Frontier chosen: {nx}, {ny} with prob: {best_prob}")
        else:
            nx, ny = next_move
        
    #if the agent has gold return to 0, 0
    else:
        nx, ny = 0, 0
        
    if myworld.agent_has_gold and myworld.agent_x == 0 and myworld.agent_y == 0:
        return Action.CLIMB
        
    if not go_forward:
        turn = determine_turn(myworld, nx, ny)
        if turn is not None:
            return turn 
        
    go_forward = False
    adjust_coordinates(myworld)
    return Action.GOFORWARD


def PyAgent_GameOver(score):
    """ PyAgent_GameOver: called at the end of each try """
    print("PyAgent_GameOver: score = " + str(score))