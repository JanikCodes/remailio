class Reminder:
    def __init__(self, id, db):
        res = db.get_block(idBlock=id)
        self.__id = res[0]
        self.__name = res[1]
        self.__block_type = res[2]
        self.__solid = res[3]
        self.__emoji = res[4]
        self.__x = 0
        self.__y = 0

    def set_x_pos(self, x):
        self.__x = x

    def set_y_pos(self, y):
        self.__y = y

