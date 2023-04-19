import random


class Point:
    def __init__(self, idx):
        self.idx = 0;
        self.neighbors = [];

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def add_neighbor_list(self, neighbor_list):
        self.neighbors = neighbor_list


class Terrain:
    def __init__(self, resource, num, point_li):
        self.resource = resource
        self.num = num
        # self.harbor = []
        self.point = point_li

    def create_element(self, resource, num, point_li):
        self.resource = resource
        self.num = num
        # self.harbor = harbor_li
        self.point = point_li


class Player:
    def __init__(self):
        """
        vp represent the victory point the player get.
        reachable_points stores all points the player could build a road as start or build a building
        settlements stores all points that have a settlement
        cities stores all points that have city
        """
        self.vp = 0  # victory points
        self.reachable_points = []
        self.settlements = []
        self.cities = []
        self.resources_list = [0,0,0,0,0]

    def build_settlements(self, point):
        self.settlements.append(point)

    def upgrade_cities(self, point):
        if point in self.settlements:
            self.settlements.remove(point)
            self.cities.append(point)

    def check_resource(self, resource_id: int):
        """
        Check the number of specific resource
        :param resource_id: the id of resources
          Dessert: Resource number 0, Produce Nothing, 1 in total
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