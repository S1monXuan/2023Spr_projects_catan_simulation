import random


class Block:
    def __init__(self):
        self.resource = 0
        self.num = 0
        self.border = []
        self.point = []

    def create_element(self, resource, num, border_li, point_li):
        self.resource = resource
        self.num = num
        self.border = border_li
        self.point = point_li


class Player:
    def __init__(self):
        self.vp = 0  # victory points
        self.roads = []
        self.settlements = []
        self.cities = []
        self.resources_list = []

    def build_settlements(self, point):
        self.settlements.append(point)

    def upgrade_cities(self, point):
        if self.settlements.__contains__(point):
            self.settlements.remove(point)
            self.cities.append(point)

    def check_resource(self, resource_id: int):
        """
        Check the number of specific resource
        :param resource_id: the id of resources
          Hills: Resources number 1, Produce Brick, 3 in total
          Forest: Resources number 2, Produce Lumber, 4 in total
          Mountains: Resources number 3, Produce Ore, 3 in total
          Fields: Resources number 4, Produce Grain, 4 in total
          Pasture: Resources number 5, Produce Wool, 4 in total
        :return: the number of specific resources
        """
        return self.resources_list[resource_id - 1]

    def trade(self, resource_id_have: int, resource_id_want: int, trade_type: int):
        """
        Trade functions helps process trade function
        :param resource_id_have: The type of resource player HAVE, the number would decrease
        :param resource_id_want: The type of resource player WANT, the number would increase
        :param trade_type: Trade type
            3: trade without any harbor, trading rate: 4 : 1
            2: trade when having a generic harbor
            1: trade when having a specific harbor

        :return: nothing, but the resources_list would change due to the trade process
        """
        self.resources_list[resource_id_want] += 1

        if trade_type == 3:
            self.resources_list[resource_id_have] -= 4
        elif trade_type == 2:
            self.resources_list[resource_id_have] -= 3
        elif trade_type == 1:
            self.resources_list[resource_id_have] -= 2