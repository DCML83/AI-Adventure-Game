import sys              # used for file reading
import random
import character
from settings import *  # use a separate file for all the constant settings


from heapq import heappush, heappop

# the class we use to store the map, and make calls to path finding
class Grid:
    # set up all the default values for the frid and read in the map from a given file
    def __init__(self, filename):
        # 2D list that will hold all of the grid tile information
        self.__grid = []
        self.__AStar = AStar(self)
        self.__load_data(filename)
        self.__width, self.__height = len(self.__grid), len(self.__grid[0])
        self.__conn = [[[0 for j in range(self.__height)] for i in range(self.__width)] for k in range(MAX_SIZE+1)]
        self._legal_m = [[[set() for j in range(self.__height)] for i in range(self.__width)] for k in range(MAX_SIZE+1)]
        self.connectiveSector()
        self.zero_value= [[0 for j in range(self.__height)] for i in range(self.__width)]
        self.__walkable = self.get_walkable()
        self.enemieslocation = set()
        self.set_enemies_location(self.__generate_random(ENEMIES))
        self.__enemies = self.init_enemies(self.enemieslocation)
        self.__enemies_value = self.set_value_grid(self.__enemies)
        self.potionslocation =set()
        self.set_potions_location(self.__generate_random(POTIONS))
        self.__potions = self.init_potions(self.potionslocation)
        self.__potions_value = self.set_value_grid(self.__potions)

    # loads the grid data from a given file name
    def __load_data(self, filename):
        # turns each line in the map file into a list of integers
        temp_grid = [list(map(int,line.strip())) for line in open(filename, 'r')]
        # transpose the input since we read it in as (y, x)
        self.__grid = [list(i) for i in zip(*temp_grid)]

     
    def init_enemies(self, locations):
        enemies =[]
        for rp in locations:
            c = character.Enemy(rp)
            enemies.append(c)
        return enemies   
    def set_enemies_location(self,location):
        self.enemieslocation = location

    def set_potions_location(self,location):
        self.potionslocation = location

    def init_potions(self, locations):
        potions =[]
        for rp in locations:
            c = character.Potion(rp)
            potions.append(c)
        return potions


    # return the cost of a given action
    # note: this only works for actions in our LEGAL_ACTIONS defined set (8 directions)
    def get_action_cost(self, action):
        return CARDINAL_COST if (action[0] == 0 or action[1] == 0) else DIAGONAL_COST

    # returns the tile type of a given position
    def get(self, tile): return self.__grid[tile[0]][tile[1]]
    def width(self):     return self.__width
    def height(self):    return self.__height
    def enemies(self):   return self.__enemies
    def potions(self):   return self.__potions
    def get_enemies_value(self): return self.__enemies_value
    def get_potions_value(self): return self.__potions_value
    def get_enemy_value(self, tile): return self.__enemies_value[tile[0]][tile[1]]
    def get_potion_value(self,tile): return self.__potions_value[tile[0]][tile[1]]
    def get_walkable(self): return self.__walkable 
    def get_enmies_location(self): return self.enemieslocation
    def get_potions_location(self): return self.potionslocation
    def remove_enemies(self,enemy): self.__enemies.remove(enemy); self.enemieslocation.remove(enemy.get_position()) 
    def remove_potions(self,potion): self.__potions.remove(potion); self.potionslocation.remove(potion.get_position()) 
    # checks if two tile are the same
    def same_tile(self, s, f): return self.get(s) == self.get(f)
    #return the sector integers of a give positon
    def get_sector(self,pos,size): return self.__conn[size][pos[0]][pos[1]]
    #assign a sector integers to a give positon
    def set_sector(self, pos,size,numSect): self.__conn[size][pos[0]][pos[1]] = numSect

    def get_legal_action(self, pos,size): return self._legal_m[size][pos[0]][pos[1]]

    # compute legal movement for each given tile
    def legal_movement(self,start,size):
        for action in LEGAL_ACTIONS:
            x = action[0]
            y = action[1]
            next_move = (start[0] + x, start[1] + y)
            if self.check_tiles(next_move,size,self.get(start)):
                if self.get_action_cost(action) == DIAGONAL_COST:
                    if self.is_connected((start[0]+x, start[1]+0),start,size) and self.is_connected((start[0]+0, start[1]+y), start,size):
                        self.get_legal_action(start,size).add(action)
                else:
                    self.get_legal_action(start,size).add(action)
    # uses breath first search to compute the distance between walkable tile to each goal tile            
    def set_value_grid(self, arr_obj):
        value = [[0 for j in range(self.__height)] for i in range(self.__width)]
        for ele in arr_obj:
            e = ele.get_position()
            value[e[0]][e[1]] = 0 
            openlist =[]
            closelist = set()
            heappush(openlist,(value[e[0]][e[1]],e))
            i =1
            while openlist:
                start = heappop(openlist)[1]
                if start in closelist: continue
                closelist.add(start)
                for action in LEGAL_ACTIONS:
                    move = (start[0]+action[0],start[1]+action[1])
                    if move in closelist: continue
                    if self.is_connected(e, move, 1):
                        if value[move[0]][move[1]] != 0 and value[start[0]][start[1]] + 1 > value[move[0]][move[1]]:continue
                        value[move[0]][move[1]] = value[start[0]][start[1]] + 1
                        heappush(openlist, (value[move[0]][move[1]],move))
        return value

                
    def get_walkable(self):
        walkable = []
        for y in range(self.height()):
            for x in range(self.width()):
                if( self.get((x,y)) == 3):walkable.append((x,y))
        return walkable
    # generate random postion for enemy and potion on the grid
    def __generate_random(self, num):
        walkable = self.__walkable
        randpoints = set()
        while len(randpoints) < num:
            rp = random.choice(walkable)
            randpoints.add(rp)
        return randpoints

   # check all other tiles for current tile surface 
    def check_tiles(self, start,size, tiletype):
        if not (start[0] >= 0 and start[1] >= 0 and start[0] < self.width() and start[1] < self.height()): return False
        for i in range(size):
            for j in range(size):
                tile = (start[0]+i, start[1]+j)
                if tile[0] >= 0 and tile[1] >=0 and tile[0] < self.width() and tile[1] < self.height():
                    if self.get(tile) != tiletype:
                        return False
                else:
                    return False
        return True

    # recusive depth first search to flood fill the connective area among all tile
    def dfs(self,start,size,type,numSect):
        cardinal = [(0, -1),(-1,  0),(1,  0),(0,  1)]
        if self.check_tiles(start,size, type) == False: return
        if self.__conn[size][start[0]][start[1]] != 0: return
        self.set_sector(start,size,numSect)
        # depth first search will expand in 4 directions
        for action in cardinal:
            move = (start[0]+action[0],start[1]+action[1])
            self.dfs(move,size,self.get(start),numSect)

    # flood fill the entire map and assign sector with different integers
    def connectiveSector(self):
        numSect = 1
        for s in range(1,len(self.__conn)): # loop from size 1 to 3
            for j in range(len(self.__conn[s])):
                for k in range(len(self.__conn[s][j])):
                    # compute legal movement for every tile
                    self.legal_movement((j,k),s)
                    # search for sector 0 and flood fill with assigned sector number
                    if self.get_sector((j,k),s)!= 0: continue
                    # flood fill the sector map with different sector number
                    self.dfs((j,k),s,self.get((j,k)),numSect)
                    numSect = numSect + 1
            numSect=1
      

    # returns true of an object of a given size can navigate from start to goal
    def is_connected(self, start, goal, size):
        # start and goal must be same type
        if not self.same_tile(start,goal): return False
        # if start sector is 0, mean is not walkable
        if self.get_sector(start,size) == 0: return False
        # make sure start and goal have the same sector
        if self.get_sector(start,size) == self.get_sector(goal,size):return True
        else: return False
    
    # heuristic function for the Astar alogrithm
    def estimate_cost(self, start, end):
        dx = abs(start[0]-end[0])
        dy = abs(start[1]-end  [1])
        cost = (CARDINAL_COST*(dx+dy)+(DIAGONAL_COST-2*CARDINAL_COST)* min(dx,dy))
        return cost

    # returns a path from start tile to finish tile
    def get_path(self, start, health, size):
        
        if self.is_connected(start,start,size) == False:
            return [], 0, set(), (start)
        else:
            if health > HEALTH_WARNING or len(self.__potions) == 0:
                path, closed , end = self.__AStar.Search(start, self.enemieslocation,self.__enemies_value,size)
                return path, sum(map(self.get_action_cost, path)),closed, end
            else:
                path, closed , end = self.__AStar.Search(start, self.potionslocation,self.__potions_value, size)
                return path, sum(map(self.get_action_cost, path)),closed, end
    #just used for testing with zero heuristic
    def get_path_zero(self, start, health, size):
        if self.is_connected(start,start,size) == False:
            return [], 0, set(), (start)
        else:
            if health > HEALTH_WARNING or len(self.__potions) == 0:
                path, closed , end = self.__AStar.Search(start, self.enemieslocation,self.zero_value,size)
                return path, sum(map(self.get_action_cost, path)),closed, end
            else:
                path, closed , end = self.__AStar.Search(start, self.potionslocation,self.zero_value, size)
                return path, sum(map(self.get_action_cost, path)),closed, end
    

###############################################################################################
# A* class 
class AStar:

    #Initializes the AStar class and passes a reference of the grid class
    def __init__(self, grid):
        self.__grid = grid 

    #constructs the path form a given node to its parent
    def reconstruct_path(self, node):
        path = []
        while node.parent != None:
            path.insert(0,node.action)
            node = node.parent
        return path

    #expand a list of child based on their LEGAL_ACTIONS
    def expand(self, node,size):
        q=[]
        state = node.state
        for action in self.__grid.get_legal_action(state,size):
            child = (state[0]+action[0], state[1]+action[1])
            n = Node(child)
            n.action = action
            n.parent = node
            n.g = node.g + self.__grid.get_action_cost(action)
            q.append(n)
        return q

    # scan the openlist and check if there were a node with less g cose
    def node_in_open(self, openlist,child):
        for n in range(len(openlist)):
            if openlist[n][2].state == child.state and openlist[n][2].g <= child.g:
                 return True

    # A* search algorithm
    def Search(self, start,goal,value, size):
        closed = set()
        openlist =[]
        s = Node(start)
        s.f =  value[s.state[0]][s.state[1]] # getting the value on given positon
        item =(s.f, s.g, s)
        heappush(openlist,item)
        while openlist:
            # Find the lowest cost node in the list
            node = heappop(openlist)[2]
            # if it is the node we want, return it
            if (node.state in goal):
                return self.reconstruct_path(node),closed, node.state
            if node.state in closed: continue
            # remove suboptimal nodes from the openlist and add them to the closedlist
            closed.add(node.state)
            for child in self.expand(node,size):
                # Caculate g and h score to find f score
                if child.state in closed: continue
                child.f = child.g + (value[child.state[0]][child.state[1]])*100
                if self.node_in_open(openlist,child) == True:continue
                # Update openlist with lowest cost
                item = (child.f, child.g, child)
                heappush(openlist,item)

####################################################################################
### Node class 
class Node:
    #Initializes the Node Class with variables
    def __init__(self, tile):
        self.state = tile
        self.action = (0, 0)
        self.g = 0
        self.f = 0
        self.parent = None

    # Comparison method for nodes 
    def __lt__(self,other):
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f
