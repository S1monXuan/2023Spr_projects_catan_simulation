class Point:
    def __init__(self, idx):
        self.idx = 0
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def add_neighbor_list(self, neighbor_list):
        self.neighbors = neighbor_list


class Terrain:
    def __init__(self, resource, num, point_li):
        self.resource = resource
        self.num = num
        self.point = point_li

    def create_element(self, resource, num, point_li):
        self.resource = resource
        self.num = num
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
        self.reachable_points = []  # points connected via roads
        self.settlements = []
        self.cities = []
        self.resources_list = [0, 0, 0, 0, 0]
        self.road_num = 0
        self.strategy = ""

    def set_resource_list(self, resource_list):
        self.resources_list = resource_list

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
          Dessert: Resource number 5, Produce Nothing, 1 in total
          Hills: Resources number 0, Produce Brick, 3 in total
          Forest: Resources number 1, Produce Lumber, 4 in total
          Mountains: Resources number 2, Produce Ore, 3 in total
          Fields: Resources number 3, Produce Grain, 4 in total
          Pasture: Resources number 4, Produce Wool, 4 in total

        :return: the number of specific resources
        """
        return self.resources_list[resource_id - 1]

    def get_max(self, resource_list):
        num = -1
        idx = -1
        for resource_idx in resource_list:
            if self.resources_list[resource_idx] > num:
                num = self.resources_list[resource_idx]
                idx = resource_idx
        return num, idx

    def discard_one_resource(self):
        if self.strategy == "settlement_prefer" or self.strategy == "harbor_prefer":
            resource_need = [0, 1, 3, 4]
            resource_latent = [2]
        elif self.strategy == "city_prefer":
            resource_need = [2, 3]
            resource_latent = [0, 1, 4]

        # get_max_id in rsource_latent:
        max_num, max_idx = self.get_max(resource_latent)

        # check the file in resource needed if all resource_latent was used
        if max_num == 0:
            max_num, max_idx = self.get_max(resource_need)
        self.resources_list[max_idx] -= 1

    def print_player(self):
        print(f'player vp: {self.vp}, settlement list: {self.settlements}, city list: {self.cities} \n'
              f'reachable points list: {self.reachable_points} \n'
              f'resources list: {self.resources_list}')


class ResourceDict:
    def __init__(self, resource_type: str):
        self.needed_dict = {0: 1, 1: 1} if resource_type == "road" else {0: 1, 1: 1, 3: 1, 4: 1} if \
            resource_type == "settlement" else {2: 3, 3: 2}
        self.resource_list = [2, 3, 4] if resource_type == "road" else [2] if \
            resource_type == "settlement" else [0, 1, 4]
        self.target_list = [0, 1] if resource_type == "road" else [0, 1, 3, 4] if \
            resource_type == "settlement" else [2, 3]


class RecordList:
    def __init__(self, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec):
        self.vp_rec = vp_rec
        self.set_rec = set_rec
        self.city_rec = city_rec
        self.road_rec = road_rec
        self.brick_rec = brick_rec
        self.lum_rec = lum_rec
        self.ore_rec = ore_rec
        self.grain_rec = grain_rec
        self.wool_rec = wool_rec


class ResRecoder:
    def __init__(self, used_round, gamePass):
        self.used_round = used_round
        self.gamePass = gamePass
