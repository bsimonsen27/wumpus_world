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
        

# class to help organize the wumpus world
class World:
    def __init__(self, size):
        self.size = size
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.agent_x = 0
        self.agent_y = 0
        self.agent_orientation = Orientation.RIGHT
        self.agent_has_gold = False
        

# function for interpreting percepts
def update_knowledge_from_percepts(world, x, y, breeze, stench):
    cell = world.grid[x][y]
    cell.visited = True
    cell.breeze = breeze
    cell.stench = stench

    if breeze:
         for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
             nx, ny = x + dx, y + dy
             if 0 <= nx < world.size and 0 <= ny < world.size:
                 if not world.grid[nx][ny].visited and not world.grid[nx][ny].safe:
                     world.grid[nx][ny].pit = True
                     
    if stench:
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.size and 0 <= ny < world.size:
                if not world.grid[nx][ny].visited and not world.grid[nx][ny].safe:
                    world.grid[nx][ny].wumpus = True
                    
    if not breeze and not stench:
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.size and 0 <= ny < world.size:
                world.grid[nx][ny].safe = True
                
    if world.grid[x][y].visited:
        world.grid[x][y].safe = True

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
                    print(f"1{nx},{ny}")
                    return nx, ny
                visited.add((nx, ny))
                queue.append((nx, ny))
    return None


# function to determine which way the agent needs to turn to be facing in the target direction
def determine_turn(world, target_x, target_y):
    agent_x, agent_y = world.agent_x, world.agent_y
    orientation = world.agent_orientation

    # Determine the orientation of the target relative to the agent
    if target_x < agent_x:
        target_orientation = Orientation.DOWN
    elif target_x > agent_x:
        target_orientation = Orientation.UP
    elif target_y > agent_y:
        target_orientation = Orientation.RIGHT
    else:
        target_orientation = Orientation.LEFT

    # Check if the direct path to the target is safe
    if (target_orientation == Orientation.DOWN and world.grid[agent_x - 1][agent_y].safe) or \
       (target_orientation == Orientation.UP and world.grid[agent_x + 1][agent_y].safe) or \
       (target_orientation == Orientation.RIGHT and world.grid[agent_x][agent_y + 1].safe) or \
       (target_orientation == Orientation.LEFT and world.grid[agent_x][agent_y - 1].safe):
        # If the direct path is safe, turn directly to the target
        print(f"orientation{orientation} target {target_orientation}")
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
                        return determine_turn(world, agent_x,ny)
        elif target_orientation == Orientation.LEFT or target_orientation == Orientation.RIGHT:
            for dx in [-1, 1]:
                nx = agent_x + dx
                if 0 <= nx < world.size:
                    if world.grid[nx][agent_y].safe:
                        return determine_turn(world,nx,agent_y)
                    
                    
# function to adjust the agents x,y position on movement
def adjust_coordinates(world):
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


def PyAgent_Process(stench, breeze, glitter, bump, scream):
    """ PyAgent_Process: called with new percepts after each action to return the next action """
    global myworld
    
    # Update world knowledge with new percepts
    update_knowledge_from_percepts(myworld, myworld.agent_x, myworld.agent_y, breeze, stench)
    
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
    
    if glitter == 1:
        myworld.agent_has_gold = True 
        return Action.GRAB

    
    # Get the next move from the path
    if not myworld.agent_has_gold:
        next_move = choose_next_move(myworld)
        #condition needs to be rewritten, this is when the next move is not found consider using cell.pit and cell.wumpus
        #which is currently not in use
        if next_move is None:
            return Action.GOFORWARD
        
        nx, ny = next_move
        
    #if the agent has gold return to 0, 0
    else:
        nx, ny = 0, 0
    print(f"x,y {myworld.agent_x} {myworld.agent_y}")
    if myworld.agent_has_gold and myworld.agent_x == 0 and myworld.agent_y == 0:
        return Action.CLIMB
        
    print(f"nx{nx}, ny{ny}")
    turn = determine_turn(myworld, nx, ny)
    if turn is not None:
        return turn 
        
    
    adjust_coordinates(myworld)
    return Action.GOFORWARD


def PyAgent_GameOver(score):
    """ PyAgent_GameOver: called at the end of each try """
    print("PyAgent_GameOver: score = " + str(score))
