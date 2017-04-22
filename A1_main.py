import sys              # used for file reading
import time             # used for timing the path-finding
import random
import pygame as pg     # used for drawing / event handling
from settings import *  # use a separate file for all the constant settings
import battle_scene
import Astar_Grid     # the A* grid class
import character
import RL_grid

class PathFindingDisplay:
    def __init__(self, mapfile):
        # initialize pygame library things
        pg.init()
        pg.display.set_caption(TITLE)
        pg.key.set_repeat(500, 100)
        self.__map        = mapfile
        self.__grid       = Astar_Grid.Grid(mapfile)
        # declare the remaining variables we'll need for the GUI
        self.__width      = self.__grid.width() * TILE_SIZE
        self.__height     = self.__grid.height() * TILE_SIZE
        self.__screen     = pg.display.set_mode((self.__width, self.__height))
        self.__font       = pg.font.SysFont(FONT_NAME, FONT_SIZE, bold=FONT_BOLD)
        self.__clock      = pg.time.Clock()
        self.__m_down     = [False]*3 # which mouse button is being held down
        self.__m_tile     = (-1, -1)  # tile the mouse is currently on
        self.__g_tile     = (-1, -1)  #goal tile after mouse click
        self.__s_tile     = (-1, -1)  # start tile for path finding
        self.__o_size     = 1        # the size of the object to pathfind
        self.__path       = []        # previous computed path
        self.__path_cost  = 0         # previous computed path cost
        self.__expanded   = set()     # previous computed set of nodes expanded
        self.__path_time  = 0         # previous path computation time
        self.__heuristic  = 0         # previous computed heuristic value
        self.__updatetime = 0
        self.__RLupdatetime = 0
        self.__astar_atuo = False
        self.__find = False
        self.__RLmove = False
        self.moves =[]
        self.__map_surface = pg.Surface((self.__width, self.__height))
        pg.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
        pg.init() 
        pg.mixer.music.load(BACKGROUND_MUSIC)
        pg.mixer.music.set_volume(BACKGROUNDS_VOLUMN)
        self.heal = pg.mixer.Sound(HEAL)
        self.fight = pg.mixer.Sound(FIGHT)
        self.gameover = pg.mixer.Sound(GAME_OVER)
        self.lightsound = pg.mixer.Sound(LIGHTING_SOUND)
        for x in range(self.__grid.width()):
            for y in range(self.__grid.height()):
                self.__draw_tile(self.__map_surface, (x,y), TILE_COLOR[self.__grid.get((x,y))], 1)
        self.__Player     = character.Player(random.choice(self.__grid.get_walkable()))      
        self.__RL_grid    = RL_grid.Grid(mapfile,self.__grid.enemies(), self.__grid.potions(), self.__Player.get_current_health())
        self.__battle_screen = pg.image.load(FULL_MOON)
        self.__start = pg.image.load(INTRO_BACK)
        self.__intro_kris = pg.image.load(INTRO_KRIS)
        self.__lightning = pg.image.load(LIGHTNING)
        self.__intro = True
        pg.mixer.music.play(-1)

    
    # game main loop update function
    def update(self):
        self.__events()             # handle all mouse and keyboard events
        if self.__astar_atuo and len(self.__grid.enemies())!=0: #check is the player press auto play
            if self.__find:
                self.__compute_path() # compute a path if we need to
                self.__find= False
                self.__RLmove = False

        if(len(self.__path) != 0) and self.is_timeout(self.__updatetime, time.clock()):#if a path is compute, player will walk towards it
            self.__update_postition(self.__path.pop(0))
            self.__updatetime=time.clock()
        #check is RL algorithm is on, the process the update base on each policy
        if self.__RLmove and self.is_timeout(self.__RLupdatetime, time.clock()) and not self.__Player.get_encounter():
            self.RL_update()
            self.__RLupdatetime=time.clock() 
        # check if the player meeting a enemy or not
        if not self.__Player.get_encounter():
            self.__encounter = (False, -1)
            if self.__Player.is_dead() ==False:# check if the game is over 
                self.__draw()               # draw everything to the screen
            else:
                self.__draw_endgame()# drawing end game screen
                self.__astar_atuo = False

        elif self.__encounter[0]:# check the player is fight, then draw the battle scence
            #print("This", self.__encounter[0])
            enemy = self.__grid.enemies()[self.__encounter[1]]
            battle_scene.Battle(self.__Player,enemy ,self.__screen)
            # if the player win, return the main screen and remove the enemy from grid world
            if self.__grid.enemies()[self.__encounter[1]].is_dead():
                    self.__grid.remove_enemies(enemy)
                    if self.__RLmove:
                        self.__RL_grid    = RL_grid.Grid(self.__map,self.__grid.enemies(), self.__grid.potions(), self.__Player.get_current_health())
                        self.RL_compute()
                    self.__Player.set_position(self.__s_tile)
                    self.__draw_tile(self.__map_surface, self.__Player.get_position(),LIGHT_GREY,1)
                    self.__Player.set_encounter(False)
                    self.__find=True

            # if self.__Player.is_dead():
            #     self.__draw_endgame()

    def game_intro(self):
        while self.__intro:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                    quit()
            # clock = pg.time.Clock()        
            self.__screen.blit(self.__start, (0,0))
            self.__screen.blit(self.__intro_kris, (self.__width/2 - 50,280))
            #self.__screen.blit(self.__intro_img, (10, 30))
            largeText = pg.font.Font('freesansbold.ttf',115)
            smallText = pg.font.Font("freesansbold.ttf",20)
            textSurf, textRect = self.text_objects("(c) ShawnKris Productions", smallText)
            textRect.center = ( (self.__width/2), (650+(50/2)) )
            self.__screen.blit(textSurf, textRect)
            self.button("Start Game",self.__width/2-150,self.__height-200,100,50,WHITE,BLUE,self.start_game)
            self.button("Quit",self.__width/2+50, self.__height-200,100,50,WHITE,RED,self.__quit)
            pg.display.update()
            # clock.tick(15)

    def start_game(self):
        self.__screen.blit(self.__lightning, (280,0))
        self.lightsound.play()
        self.__intro = False   

    def main_memu(self):
        self.restart()
        self.__intro = True            

    # draw main game to the screen
    def __draw(self):
        self.__screen.blit(self.__map_surface, (0,0))
        self.__draw_path()
        self.__draw_grid_lines()
        self.__draw_value(self.__get_tile(pg.mouse.get_pos()))
        # self.__draw_stats()
        self.__draw_character_info()
        self.__draw_enemies()
        self.__draw_potions()
        self.__draw_player()
        pg.display.flip()
    #function to draw game over screen
    def __draw_endgame(self):
        self.__screen.blit(self.__map_surface, (0,0))
        smallText = pg.font.SysFont("comicsansms",50)
        label = smallText.render("Game Over", 1, RED)
        self.__screen.blit(label, (self.__width/2-100, self.__height/2-20))
        # self.gameover.play()
        self.button("Restart",100,self.__height-200,100,50,WHITE,YELLOW,self.restart)
        self.button("Main Menu",self.__width/2-50,self.__height-200,100,50,WHITE,BLUE,self.main_memu)
        self.button("Quit",self.__width-200, self.__height-200,100,50,WHITE,RED,self.__quit)                
        pg.display.flip()
    #draw popup text indicate the player is in battle mode
    def __draw_battle(self):
        self.__screen.blit(self.__map_surface, (0,0))
        self.__screen.blit(self.__battle_screen, (0,self.__height/4))
        pg.display.flip()


    # draw the path and expanded tiles
    def __draw_path(self):
        # draw nodes from the satrt tile following the path to the goal tile
        current = self.__s_tile[:]
        for action in self.__path:
            self.__draw_tile(self.__screen, current, WHITE, self.__o_size)
            current = (current[0] + action[0], current[1] + action[1])

        # draw the path start and end tiles
        self.__draw_tile(self.__screen, self.__m_tile, WHITE, self.__o_size)
        if self.__s_tile != (-1, -1): self.__draw_tile(self.__screen, self.__s_tile, YELLOW, self.__o_size)
    
    #draw the enemies tile on screen
    def __draw_enemies(self):
        color = PURPLE
        if (time.clock() - self.__updatetime)*1000 > COLOR_UPDATE:
            color = (255, random.randint(1,255), 255-random.randint(1,255))
            self.__updatetime = time.clock()
        for enemy in self.__grid.enemies():
            self.__draw_tile(self.__screen, enemy.get_position(), color, 1)
    # draw potions tile on screen with red  
    def __draw_potions(self):
        for potion in self.__grid.potions():
            self.__draw_tile(self.__screen, potion.get_position(), RED, 1)
    # draw character info on screen
    def __draw_character_info(self):
        self.__draw_text(self.__Player.get_name(), (10,10), FONT_COLOR)
        pg.draw.rect(self.__screen, RED,[10,30,self.__Player.get_current_health()*10,10])
        self.__draw_text(str(self.__Player.get_current_health())+"/"+str(self.__Player.get_max_health()), (10,50), FONT_COLOR)
        pg.draw.rect(self.__screen, WHITE,[10,30,self.__Player.get_max_health()*10,10],2)
        self.__draw_text("Attack:"+ str(self.__Player.get_attack()), (10, 70), FONT_COLOR)
        self.__draw_text("Current Position:"+str(self.__Player.get_position()), (10,90), FONT_COLOR)

    # time out function for postition update
    def is_timeout(self, start, current):
        if (current-start)*1000 > 300:
            return True
        return False
    # draw value grid heuristic when mouse is hover a goal tile
    def __draw_value(self, tile):
        for potion in self.__grid.potions():
            if tile == potion.get_position():
                for x in SHOW_VALUE_GRID_SIZE:
                    for y in SHOW_VALUE_GRID_SIZE:
                        a = tile[0] + x
                        b = tile[1] + y
                        if a >= 0 and b >= 0 and a < self.__grid.width() and b < self.__grid.height():
                            center = (int(a*TILE_SIZE)+2, int(b*TILE_SIZE)+2)
                            self.__draw_tile(self.__screen, (a,b), BLACK,1)
                            if self.__grid.get_potion_value((a,b))!=0:
                                self.__draw_text(str(self.__grid.get_potion_value((a,b))), center, FONT_COLOR)
                        else:
                            continue



        for enemy in self.__grid.enemies():
            if tile == enemy.get_position():
                for x in SHOW_VALUE_GRID_SIZE:
                    for y in SHOW_VALUE_GRID_SIZE:
                        a = tile[0] + x
                        b = tile[1] + y
                        if a >= 0 and b >= 0 and a < self.__grid.width() and b < self.__grid.height():
                            center = (int(a*TILE_SIZE)+2, int(b*TILE_SIZE)+2)
                            self.__draw_tile(self.__screen, (a,b), BLACK,1)
                            if self.__grid.get_enemy_value((a,b))!=0:
                                self.__draw_text(str(self.__grid.get_enemy_value((a,b))), center, FONT_COLOR)
                        else:
                            continue



               
    #draw player tile
    def __draw_player(self):
        self.__s_tile = self.__Player.get_position()
        if self.__s_tile != (-1, -1): self.__draw_tile(self.__screen, self.__s_tile, YELLOW, self.__o_size)
    # update player position base on action
    def __update_postition(self, action):
        player_position = self.__Player.get_position()
        new_postion = player_position[0] + action[0], player_position[1] + action[1]
        #make sure player can walk over the unwalkable tile
        if self.__grid.is_connected(new_postion, player_position, self.__o_size):
            self.__Player.set_position((player_position[0] + action[0], player_position[1] + action[1]))
       
        for potion in self.__grid.potions():
            if self.__Player.get_position() == potion.get_position():
                self.heal.play()
                self.__Player.healing(potion)
                self.__grid.remove_potions(potion)
                self.__draw_tile(self.__map_surface, self.__Player.get_position(),LIGHT_GREY,1)
                self.__find=True
                if self.__RLmove:
                    self.__RL_grid    = RL_grid.Grid(self.__map,self.__grid.enemies(), self.__grid.potions(), self.__Player.get_current_health())
                    self.RL_compute()


        for enemy in self.__grid.enemies():
            if self.__Player.get_position() == enemy.get_position():
                self.fight.play()
                self.__draw_battle()
                pg.time.wait(2000)
                self.__Player.set_encounter(True)
                self.__draw_tile(self.__map_surface, self.__Player.get_position(),LIGHT_GREY,1)
                self.__encounter = (self.__Player.get_encounter(), self.__grid.enemies().index(enemy))
        

    # draw the grid lines
    def __draw_grid_lines(self):
        for x in range(self.__grid.width()):
            pg.draw.line(self.__screen, GRID_COLOR, (x*TILE_SIZE, 0), (x*TILE_SIZE, self.__height))
        for y in range(self.__grid.height()):
            pg.draw.line(self.__screen, GRID_COLOR, (0, y*TILE_SIZE), (self.__width, y*TILE_SIZE))

    # computes and stores a path if we have the left mouse button held down
    def __compute_path(self):
        self.__path, self.__path_cost, self.__expanded, self.__path_time, self.__heuristic = [], 0, set(), 0, 0
        t0 = time.clock()
        self.__path, self.__path_cost, self.__expanded, end_tile= self.__grid.get_path(self.__s_tile, self.__Player.get_current_health(),self.__o_size)
        self.__heuristic = self.__grid.estimate_cost(self.__s_tile, end_tile)
        self.__path_time = time.clock()-t0
    # draw all the tiles with values and policy
    def __draw_RL_tiles(self):
        for r in range(self.__RL_grid.rows()):
            for c in range(self.__RL_grid.cols()):
                # if the tile is not walkable, just draw a grey tile
                if self.__RL_grid.get_state(r,c) != STATE_WALKABLE:
                    self.__draw_tile(self.__map_surface, (c, r), TILE_COLOR[self.__grid.get((c,r))], 1)
                # otherwise we should color it based on our current value estimate
                else:
                    value = self.__RL_grid.get_value(r,c)
                    color = [100, 100, 100]
                    min, max = self.__RL_grid.get_min_value(), self.__RL_grid.get_max_value()
                    if   value < 0: color = [100, 100-abs(value/min)*100, 100-abs(value/min)*100]
                    elif value > 0: color = [100-abs(value/max)*100, 100, 100-abs(value/max)*100]
                    self.__draw_tile(self.__map_surface, (c, r), color, 1)
                    policy = self.__RL_grid.get_policy(r,c)
                    center = (int(c*TILE_SIZE + TILE_SIZE/2), int(r*TILE_SIZE + TILE_SIZE/2))
                    pg.draw.circle(self.__map_surface, BLACK, center, 2)
                    for i in range(len(LEGAL_ACTIONS)):
                        length = (TILE_SIZE/2) * (0.5 if policy[i] > 0 else 0)
                        pg.draw.line(self.__map_surface, BLACK, center, (center[0] + length*LEGAL_ACTIONS[i][1], center[1] + length*LEGAL_ACTIONS[i][0]))
    #function for RL to update current player postion
    def RL_update(self):
        player_position = self.__Player.get_position()
        playerpolicy = self.__RL_grid.get_policy(player_position[1],player_position[0])
        self.moves=[]
        for i in range(len(playerpolicy)):
            if playerpolicy[i]> 0:
                self.moves.append(i)
        action = LEGAL_ACTIONS[self.moves.pop()]
        self.__update_postition((action[1],action[0]))
    #function to compute pathes for all goals
    def RL_compute(self):
        if len(self.__grid.enemies())!=0:
            while not self.__RL_grid.is_converge():
                self.__RL_grid.update_values()
                self.__RL_grid.update_policy()
                self.__draw_RL_tiles()
            self.__RLupdatetime = time.clock()
            self.__RLmove = True
        else: self.__RLmove = False
    
       
    
    def text_objects(self,text, font):
        textSurface = font.render(text, True,BLACK)
        return textSurface, textSurface.get_rect()
    #button function to draw button on screen
    def button(self,msg,x,y,w,h,bg,ac,action=None):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pg.draw.rect(self.__screen, ac,(x,y,w,h))
            pg.draw.rect(self.__screen,BLACK,(x,y,w,h),4)

            if click[0] == 1 and action != None:
                action()         
        else:
            pg.draw.rect(self.__screen, bg,(x,y,w,h))
            pg.draw.rect(self.__screen, BLACK,(x,y,w,h),4)

        smallText = pg.font.SysFont("comicsansms",20)
        textSurf, textRect = self.text_objects(msg, smallText)
        textRect.center = ( (x+(w/2)), (y+(h/2)) )
        self.__screen.blit(textSurf, textRect)
    # draw a tile location with given parameters
    def __draw_tile(self, surface, tile, color, size):
        surface.fill(color, (tile[0]*TILE_SIZE, tile[1]*TILE_SIZE, TILE_SIZE*size, TILE_SIZE*size))

    # draws text to the screen at a given location
    def __draw_text(self, text, pos, color):
        label = self.__font.render(text, 1, color)
        self.__screen.blit(label, pos)

    # returns the tile on the grid underneath a given mouse position in pixels
    def __get_tile(self, mpos):
        return (mpos[0] // TILE_SIZE, mpos[1] // TILE_SIZE)

    # returns a pixel rectangle, given a tile on the grid
    def __get_rect(self, tile, pad):
        return (tile[0]*TILE_SIZE+pad, tile[1]*TILE_SIZE+pad, TILE_SIZE-pad, TILE_SIZE-pad)

    # called when the program is closed
    def __quit(self):
        pg.quit()
        sys.exit()
    # called when the player want to restart the game
    def restart(self):
        self.__grid  = Astar_Grid.Grid(self.__map)
        self.__Player = character.Player(random.choice(self.__grid.get_walkable()))        
    #returns a random integer, given the number of enemies
    def __generate_random(self, num):
        walkable = self.__walkable
        randpoints = set()
        while len(randpoints) < num:
            rp = random.choice(walkable)
            randpoints.add(rp)
        return randpoints
        
    # events and input handling
    def __events(self):
        self.__time_start = time.clock()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.__quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.__quit()
                if event.key == pg.K_e:
                    self.prev_sector = -1
                    self.__o_size = 1 + (self.__o_size)%MAX_SIZE
                if event.key == pg.K_p: 
                    self.RL_compute()
                if event.key == pg.K_r:
                    self.__grid  = Astar_Grid.Grid(self.__map)
                if event.key == pg.K_q:
                    if self.__astar_atuo:self.__astar_atuo = False
                    else:    
                        if len(self.__grid.enemies())>0:
                            self.__astar_atuo = True
                            self.__compute_path()
                #player mannual control key press 
                if event.key == pg.K_UP:
                    self.__update_postition(LEGAL_ACTIONS[UP])
                if event.key == pg.K_DOWN:
                    self.__update_postition(LEGAL_ACTIONS[DOWN])
                if event.key == pg.K_LEFT:
                    self.__update_postition(LEGAL_ACTIONS[LEFT])
                if event.key == pg.K_RIGHT:
                    self.__update_postition(LEGAL_ACTIONS[RIGHT])
  



            

sys.setrecursionlimit(10000)

# create the game object
g = PathFindingDisplay(MAP_FILE)
intro = True
# run the main game loop
    
while True:
    g.game_intro()
    g.update()
