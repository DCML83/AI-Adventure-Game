class player:
    def __init__(self,x,y):
        self.__health = 100
        self.__attack = 10
        self.__position = (x,y)

    def get_postion(self):
        return self.__postion
    def update_postion(self,(xy)):
        self._position = (self.__position[0]+xy[0], self.__position[1]+xy[1])

    def get_health(self):
        return self.__health
        
    def attack_enemey(self):
        return self.__attack

    def get_hurt(self, attack):
        self.__health = self.__health - attack