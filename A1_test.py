import sys              # used for file reading
import time 
import copy            # used for timing the path-finding
from settings import *  # use a separate file for all the constant settings
import Astar_Grid
import character
# set the systemn recursion limit high so that we don't worry about going over
sys.setrecursionlimit(10000)

# the start and end tiles for testing
player_location=(41,51)

player= character.Player(player_location)
zero_player = character.Player(player_location)

heuristic_grid = Astar_Grid.Grid(MAP_FILE)
#deep copy the grid world for zero heuristic
zero_grid= copy.deepcopy(heuristic_grid)

zero_total_time =0
total_time  =0
print("----------------------------------------------------------------------------")
print("|              With Value            ||            Zero Heuristic          |")
print("|--------------------------------------------------------------------------|")
while len(heuristic_grid.enemies())!=0 and len(zero_grid.enemies())!=0:
        t0 = time.clock()
        path, path_cost, expanded, end_tile= heuristic_grid.get_path(player.get_position(), player.get_current_health(),1)
        path_time = time.clock()-t0
        total_time += path_time
        player_location = player.get_position()
        player.set_position(end_tile)
        for potion in heuristic_grid.potions():
            if player.get_position() == potion.get_position():
                player.healing(potion)
                heuristic_grid.remove_potions(potion)
        for enemy in heuristic_grid.enemies():
            if player.get_position() == enemy.get_position():
                enemy.attacks(player)
                heuristic_grid.remove_enemies(enemy)


        zt0 = time.clock()
        zpath, zpath_cost, zexpanded, zend_tile= zero_grid.get_path_zero(zero_player.get_position(), zero_player.get_current_health(),1)
        zpath_time = time.clock()-zt0
        zero_total_time += zpath_time
        zplayer_location = zero_player.get_position()
        zero_player.set_position(zend_tile)
        for potion in zero_grid.potions():
            if zero_player.get_position() == potion.get_position():
                zero_player.healing(potion)
                zero_grid.remove_potions(potion)
    
        for enemy in zero_grid.enemies():
            if zero_player.get_position() == enemy.get_position():
                enemy.attacks(zero_player)
                zero_grid.remove_enemies(enemy)

        print("| %s (%3d,%3d) | %s (%3d,%3d) || %s (%3d,%3d) | %s (%3d,%3d) |" % ("Start:", player_location[0], player_location[1],"Goal:", end_tile[0], end_tile[1],"Start:", zplayer_location[0], zplayer_location[1],"Goal:", zend_tile[0], zend_tile[1]))
        print("| %s %24d || %34d |"% ("Path Cost", path_cost, zpath_cost))
        print("| %s %24d || %34d |"% ("Expanded:", len(expanded), len(zexpanded)))
        print("| %s %21f ms || %31f ms |"% ("Path Time", path_time*1000, zpath_time*1000))
        print("----------------------------------------------------------------------------")

print("---------------With Value------------||------------Zero Heuristic-----------")
print("---------------Total Time------------||--------------Total Time-------------")
print("-------------%10f ms ----------||------------%10f ms------------"%(total_time*1000, zero_total_time*1000))
print("----------------------------------------------------------------------------")

