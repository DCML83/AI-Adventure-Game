import random
from settings import *  # use a separate file for all the constant settings
import pygame as pg     # used for drawing / event handling
import Astar_Grid
import battle_scene
import time
#super class for all character in game
#those character share those common value
class Character(object): 
    def __init__(self, name, max_health, attack, postion, image):
        self.__name = name
        self.__current_health =max_health
        self.__max_health = max_health
        self.__attack = attack
        self.__position = postion
        self.__is_dying = False
        self.__image = image
        self.__playerturn = False

    def get_name(self): return self.__name
    def set_name(self, name): self.__name = name
    def get_current_health(self): return self.__current_health
    def set_current_health(self, health): self.__current_health = health
    def get_max_health(self): return self.__max_health
    def get_attack(self): return self.__attack
    def set_attack(self, att): self.__attack = self.attack
    def get_position(self): return self.__position
    def set_position(self, tile): self.__position = tile

    def get_image(self): return self.__image

    #check to see if the player is dying and needs health
    def is_dying(self, b): self.__is_dying = b
    def is_dead(self): return self.__is_dying

    def set_playerturn(self, turn): self.__playerturn = turn
    def get_playerturn(self): return self.__playerturn

#player class inherit from characher class
class Player(Character):
    def __init__(self,tile):
        hero = pg.image.load(CHARACTER)
        Character.__init__(self,"Kris", 10, 5, tile, hero)
        #check to see if the player is hurt
        self.__takes_damage = False
        #check to see if the player should run 
        self.__run = False
        self.__encounter = False
        
    def set_encounter(self, encounter): self.__encounter = encounter
    def get_encounter(self): return self.__encounter

    def healing(self, potion):#player health increase 
        current = self.get_current_health()+potion.get_health_point()
        if current > self.get_max_health():
            self.set_current_health(self.get_max_health())
        else:
            self.set_current_health(current)

    def attacks(self, enemy):
        enemyhealth = enemy.get_current_health() - self.get_attack()
        enemy.set_current_health((enemyhealth)) # enemy's health  will decrease 
        if enemy.get_current_health() <= 0: 
             enemy.is_dying(True)

class Enemy(Character):
    #initialize enemy class 
    def __init__(self, tile):
        health = random.randint(12,14)
        attack = random.randint(1,2)
        enemy_image = pg.image.load(random.choice(ENEMIES_IMAGES))
        # enemy_chosen = enemy_list[random.randint(0,2)]
        enemy_names_list = ["Warzog", "Loki", "Weezug"]
        Character.__init__(self,enemy_names_list[random.randint(0,2)], health, attack, tile, enemy_image)
        

    def attacks(self,player):
        #enemy attacks player
       playerhealth = player.get_current_health() - self.get_attack()
       player.set_current_health(playerhealth)
       if player.get_current_health() <= 1: 
             player.is_dying(True)

class Potion():
    def __init__(self, position):
        hp = random.randint(3,10)
        self.__postion = position
        self.__health_point = hp

    def get_position(self): return self.__postion
    def get_health_point(self): return self.__health_point


