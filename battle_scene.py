import pygame as pg
import character
import random
import time
import sys
from settings import *  # use a separate file for all the constant settings

class Battle:
    def __init__(self, player, enemy, screen):
        pg.key.set_repeat(3000, 100)
        self.__font = pg.font.SysFont(FONT_NAME, FONT_SIZE, bold=FONT_BOLD)
        background_colour = (100,100,100)
        self.__Enemy = enemy
        self.__Player = player
        self.__screen = screen
        self.__claw_attack = pg.image.load(CLAW)
        self.__sword_attack = pg.image.load(SWORD_IMAGE)
        background_image = pg.image.load(BG_CHOICE)
        enemy_chosen = enemy.get_image()
        hero = player.get_image()
        screen.blit(background_image, (0,0))   
        screen.blit(enemy_chosen, (100,350))
        screen.blit(hero, (600,350))
        self.__draw_character_info()
        self.__draw_enemy_info()
        self.__events()
        pg.display.flip()
        

    def __draw_text(self, text, pos, color):
        label = self.__font.render(text, 1, color)
        self.__screen.blit(label, pos)

    def __draw_character_info(self):
        self.__draw_text(self.__Player.get_name(), (600,600), FONT_COLOR)
        pg.draw.rect(self.__screen, RED,[len(list(self.__Player.get_name()))*10 + 600,600,self.__Player.get_current_health()*10,10])
        self.__draw_text(str(self.__Player.get_current_health())+"/"+str(self.__Player.get_max_health()), (self.__Player.get_max_health()*10 + 660,600), FONT_COLOR)
        pg.draw.rect(self.__screen, WHITE,[len(list(self.__Player.get_name()))*10 + 600,600,self.__Player.get_max_health()*10,10],2)

    
    def __draw_enemy_info(self):
        self.__draw_text(self.__Enemy.get_name(), (10,600), FONT_COLOR)
        pg.draw.rect(self.__screen, RED,[len(list(self.__Enemy.get_name()))*10 + 20,600,self.__Enemy.get_current_health()*10,10])
        self.__draw_text(str(self.__Enemy.get_current_health())+"/"+str(self.__Enemy.get_max_health()), (self.__Enemy.get_max_health()*10 + 100,600), FONT_COLOR)
        pg.draw.rect(self.__screen, WHITE,[len(list(self.__Enemy.get_name()))*10 + 20,600,self.__Enemy.get_max_health()*10,10],2)

    def __draw_attack(self):
        self.__screen.blit(self.__claw_attack, (600,300))

    def __draw_player_attack(self):
        self.__screen.blit(self.__sword_attack, (10,300))

        
    def __quit(self):
        pg.quit()
        sys.exit()   

    def __events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.__quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.__quit()
                if event.key == pg.K_a:
                    sword = pg.mixer.Sound(SWORD)
                    sword.play()
                    self.__Player.attacks(self.__Enemy)
                    self.__draw_player_attack()
                    if not self.__Enemy.is_dead():
                        self.__Enemy.attacks(self.__Player)
                        self.__draw_attack()
                        claw = pg.mixer.Sound(CLAWS)
                        claw.play()
            
                if event.key == pg.K_b:
                    self.__Enemy.attacks(self.__Player)
                    self.__draw_attack()
                            