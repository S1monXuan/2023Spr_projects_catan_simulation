import random
import pandas as pd
from Elements import Player, Terrain, ResourceDict, RecordList, ResRecoder
import matplotlib.pyplot as plt
import warnings
import csv
import numpy as np

warnings.filterwarnings('ignore')


def roll_dice() -> int:
    """
    Rolling a dice, would return random number between 1 - 6
    :return: Integer between 1 - 6
    >>> tst = np.array([roll_dice() for _ in range(100)])
    >>> (tst > 0).all()
    True
    >>> (tst < 7).all()
    True
    """
    return random.randint(1, 6)


def initiate_map(default_setting_url):
    """
    Would initiate a map in this simulation
    :return:list with all terrains with their unique resource and number
    """
    # step 1 read point_harbor data
    # link point_harbor using list(harbor)[list(point)]
    p_h_file = default_setting_url + 'point_harbor.csv'
    p_h_numpy = pd.read_csv(p_h_file).to_numpy()
    p_h_numpy[:, :2] -= 1

    p_h_data = list(p_h_numpy)
    # delete the first two lines

    p_h = []
    for p_h_pairs in p_h_data:
        p_h.append(list(p_h_pairs))

    # step 2 read point_point data
    # link point_point using list(point1)[list(point2)]
    p_p_file = default_setting_url + 'point_point.csv'
    p_p_data = list(pd.read_csv(p_p_file).to_numpy())
    p_p = [[] for _ in range(54)]
    # fill list with neighborList
    for [idx, h] in p_p_data:
        p_p[idx - 1].append(h - 1)
        p_p[h - 1].append(idx - 1)

    # step 3 read terrain_point data
    # link terrain_point using list(terrain)[list(point)]
    t_p_file = default_setting_url + 'terrain_point.csv'
    t_p_data = list(pd.read_csv(t_p_file).to_numpy())
    t_p = [[] for x in range(19)]
    for [idx, point] in t_p_data:
        t_p[idx - 1].append(point - 1)
    return p_h, p_p, t_p


def get_terrain_resource():
    """
    Designate resource to each terrain in random
    :return: A list of resource type of each terrain
    >>> tst = get_terrain_resource()
    >>> len(tst)
    19
    >>> tst_res = [0, 0, 0, 0, 0, 0]
    >>> for val in tst:
    ...     tst_res[val] += 1
    >>> tst_res
    [3, 4, 3, 4, 4, 1]
    """
    terrain_resource_list = [3, 4, 3, 4, 4, 1]
    res = []
    for i in range(19):
        cur = random.randint(0, 5)
        while terrain_resource_list[cur] == 0:
            cur = random.randint(0, 5)
        terrain_resource_list[cur] -= 1
        res.append(cur)
    return res


def get_roll_num_list(terrain_resource_list: list):
    """
    Return a list of roll number for each terrain
    :param terrain_resource_list: the resource type of each terrain
    :return: a list represent resource for each terrain with the same idx
    """
    roll_record_li = [0, 0, 1, 2, 2, 2, 2, 0, 2, 2, 2, 2, 1]
    res = []
    for idx in range(len(terrain_resource_list)):
        # dessert will not have a resource
        if terrain_resource_list[idx] == 5:
            res.append(7)
            continue
        # designate a number for each other terrain
        while True:
            cur_num = random.randint(2, 12)
            if roll_record_li[cur_num] != 0:
                res.append(cur_num)
                roll_record_li[cur_num] -= 1
                break
    return res


def generate_terrain_dict(terrain_type_list: list, terrain_number_list: list, terrain_point_list: list):
    """
    Generate a dictionary which key represents the idx of a terrain, value stores a terrian object
    :param terrain_type_list: list with all possible terrain type
    :param terrain_number_list: list contains number for all terrains in order
    :param terrain_point_list: list stores all points for the terrain
    :return: return a dict for idx and terrain
    """
    # create a dict to store all source with the type {roll number(int): type_list[]}
    idx_terrain_dict = {}
    res = {}
    for idx in range(len(terrain_type_list)):
        curTerrain = Terrain(resource=terrain_type_list[idx],
                             num=terrain_number_list[idx],
                             point_li=terrain_point_list[idx])
        res.setdefault(terrain_number_list[idx], []).append(curTerrain)
        idx_terrain_dict[idx] = curTerrain
    return idx_terrain_dict, res


def point_terrain_creator(tp: list, idx_terrain_dict: dict):
    """
    # create a dict for resource sufficient using terrain-point list
    :param tp: list for all terrain-point relation
    :param idx_terrain_dict: index-terrain relation dictionary
    :return: return a dict for point-terrain relation, a list stores all point probability and a sorted list for arrange
    """
    # create a dict for resource sufficient using tp
    point_terrain_dict = {}
    for terrain_id in range(len(tp)):
        for point_id in tp[terrain_id]:
            point_terrain_dict.setdefault(point_id, []).append(terrain_id)
    num_pro_list = [0, 0, 1, 2, 3, 4, 5, 0, 5, 4, 3, 2, 1]
    # calculate the possibility of each point
    point_probability = {}
    for point, terrains in point_terrain_dict.items():
        probability = 0
        for terrain_idx in terrains:
            ter_num = idx_terrain_dict[terrain_idx].num
            probability += num_pro_list[ter_num]
        point_probability[point] = probability
    # sort the point_probability dict
    point_probability_sort_list = sorted(point_probability, key=point_probability.get, reverse=True)
    return point_terrain_dict, point_probability, point_probability_sort_list


def point_buildable(point_list: list, point2: int, pp: list, reachable_list: list):
    """
    Check whether a point is buildable for point_list
    :param reachable_list: all reachable point that might be able to build a building
    :param point_list: a list for all points that have building already
    :param point2: the point that need to check
    :param pp: the point-point list to check
    :return: True if the point can build a building, False if not
    """
    not_buildable_list = []
    not_buildable_list.extend(point_list)
    for point in point_list:
        not_buildable_list.extend(pp[point])
    return point2 not in not_buildable_list


def player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict, point_probability,
                     strategy):
    """
        Generate a player using current border
    :param point_probability_sort_list: list stores all point sorted via their probability
    :param pp: point-point relation, stores all neighbors for each point
    :param point_terrain_dict: point-terrain dictionary
    :param idx_terrain_dict: index-terrain dictionary
    :param point_probability: the probability val list
    :return: a player with default 2 settlement and 2 roads
    """
    player = Player()
    # create default settlements
    # if the first two points are buildable, choose the first 2. Else choose the first and the most suitable that could be built
    point2 = 1
    def_point_list = [*range(0, 54, 1)]
    while not point_buildable([point_probability_sort_list[0]], point_probability_sort_list[point2], pp,
                              def_point_list):
        point2 += 1
    player.settlements.append(point_probability_sort_list[point2])
    player.settlements.append(point_probability_sort_list[0])
    player.reachable_points.append(point_probability_sort_list[point2])
    player.reachable_points.append(point_probability_sort_list[0])

    # get default resources:
    terrain_list = point_terrain_dict[point_probability_sort_list[0]]

    # build 2 roads for current place
    build_a_road(player, point_probability, pp, harbor_point_list, special_point=point_probability_sort_list[0])
    build_a_road(player, point_probability, pp, harbor_point_list, special_point=point_probability_sort_list[point2])

    player.vp = 2
    player.road_num = 2
    player.strategy = strategy
    print('player setting created, bellowed is the original situation ')
    player.print_player()
    return player


def compete_player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict, point_probability,
                             strategy_list) -> list:
    """
        Generate a player using current border
    :param strategy_list: a list contains all strategy each player uses
    :param point_probability_sort_list: list stores all point sorted via their probability
    :param pp: point-point relation, stores all neighbors for each point
    :param point_terrain_dict: point-terrain dictionary
    :param idx_terrain_dict: index-terrain dictionary
    :param point_probability: the probability val list
    :return: a list of player with their default status
    """
    player_num = len(strategy_list)
    player_li = [Player() for _ in range(player_num)]
    settlement_list = []
    def_point_list = [*range(0, 54, 1)]

    # Phase1 get first terrain based on their order
    for player in player_li:
        cur_point = 0
        while not point_buildable(settlement_list, point_probability_sort_list[cur_point], pp,
                                  def_point_list):
            cur_point += 1
        player.settlements.append(point_probability_sort_list[cur_point])
        player.reachable_points.append(point_probability_sort_list[cur_point])
        build_a_road(player, point_probability, pp, harbor_point_list,
                     special_point=point_probability_sort_list[cur_point])
        settlement_list.append(point_probability_sort_list[cur_point])

    for idx in range(player_num - 1, -1, -1):
        player = player_li[idx]
        cur_point = 0
        while not point_buildable(settlement_list, point_probability_sort_list[cur_point], pp,
                                  def_point_list):
            cur_point += 1
        player.settlements.append(point_probability_sort_list[cur_point])
        player.reachable_points.append(point_probability_sort_list[cur_point])
        build_a_road(player, point_probability, pp, harbor_point_list,
                     special_point=point_probability_sort_list[cur_point])

        settlement_list.append(point_probability_sort_list[cur_point])
        # get initial resource
        get_default_resource(player, idx_terrain_dict, point_probability_sort_list[cur_point])

        # set init information for this player
        player.vp = 2
        player.road_num = 2
        player.strategy = strategy_list[idx]

    for player in player_li:
        player.print_player()

    return player_li


def get_default_resource(player: Player, idx_terrain_dict: dict, default_settlement: int) -> None:
    """
        Simulatte the resource get process, after the function, all resources were updated
    :param player:
    :param terrain_dict:
    :return:
    """
    for idx, terrain in idx_terrain_dict.items():
        if (default_settlement in terrain.point) and (terrain.resource != 5):
            player.resources_list[terrain.resource] += 1
    # pass


def own_harbor(player: Player, harbor_point_list: dict) -> bool:
    """
    Check whether a player owns a harbor
    :param player: a player object
    :param harbor_point_list: a harbor stores all points with harbor
    :return: True if a player owns a harbor, False if not
    >>> p = Player()
    >>> p.settlements = [0]
    >>> p.cities = [1]
    >>> harb_list1 = [2, 3, 4, 5]
    >>> harb_list2 = [1]
    >>> harb_list3 = [0, 2, 3, 4]
    >>> own_harbor(p, harb_list1)
    False
    >>> own_harbor(p, harb_list2)
    True
    >>> own_harbor(p, harb_list3)
    True
    """
    possible_point = player.settlements.copy()
    possible_point.extend(player.cities)
    for point in possible_point:
        if point in harbor_point_list:
            return True
    return False


def get_trade_rate(player, harbor_point_list) -> int:
    """
    Return a trade rate for the current player
    :param player: Player object
    :param harbor_point_list: harbor list
    :return: 3 if player owns a harbor, 4 if player did not owns a harbor
    >>> p = Player()
    >>> p.settlements = [0]
    >>> p.cities = [1]
    >>> harb_list1 = [2, 3, 4, 5]
    >>> harb_list2 = [1]
    >>> harb_list3 = [0, 2, 3, 4]
    >>> get_trade_rate(p, harb_list1)
    4
    >>> get_trade_rate(p, harb_list2)
    3
    >>> get_trade_rate(p, harb_list3)
    3
    """
    if len(harbor_point_list) == 0:
        return 4
    return 3 if own_harbor(player, harbor_point_list) else 4


def resource_compare_generator(player, trade_rate, resDic: ResourceDict):
    """
    Calculate the turnable resources number
    :param resDic: ResourceDict contians resource dict for current resource
    :param player: palyer
    :param trade_rate: 4 without harbro, else 3
    :return: resource_lack lack number of resource, resource_turn turnable resource number
    >>> p = Player()
    >>> p.set_resource_list([1, 1, 0, 0, 0])
    >>> rd = ResourceDict("road")
    >>> resource_compare_generator(p, 3, rd)
    (0, 0)
    """
    resource_lack = 0
    resource_turn = 0  # source could get via trading
    for idx in range(5):
        # check if the needed resource is redundant
        if idx in resDic.target_list:
            if resDic.needed_dict[idx] < player.resources_list[idx]:
                resource_turn += int(max(player.resources_list[idx] - resDic.needed_dict[idx], 0) / trade_rate)
            else:
                resource_lack += max(resDic.needed_dict[idx] - player.resources_list[idx], 0)
        else:
            resource_turn += int(max(player.resources_list[idx], 0) / trade_rate)
    return resource_lack, resource_turn


def city_possible(player: Player, harbor_point_list):
    """
    Check if the current player could build a city
    :param player: Type Player
    :return: True if the player could build a city, False if not
    >>> p = Player()
    >>> p.settlements = [0]
    >>> p.set_resource_list([0, 3, 2, 2, 0])
    >>> hb1 = [0]
    >>> hb2 = [1]
    >>> rd = ResourceDict("road")
    >>> city_possible(p, hb1)
    True
    >>> city_possible(p, hb2)
    False
    """
    # check if possible grain num >= 2 and ore num >= 3
    resources_list = player.resources_list
    # check if there has settlements for upgrading
    if len(player.settlements) == 0 or len(player.cities) == 4: return False
    # check if resource is suitable without trading
    if resources_list[2] >= 3 and resources_list[3] >= 2: return True

    # check if resource is suitable with trading
    trade_rate = get_trade_rate(player, harbor_point_list)

    resDic = ResourceDict("city")

    resource_lack, resource_turn = resource_compare_generator(player, trade_rate, resDic)

    return resource_lack <= resource_turn


def settlement_possible(player: Player, harbor_point_list, pp):
    """
    Check if the current player could build a settlement
    :param harbor_point_list: list contains all harbor point
    :param player: Type Player
    :return: True if the player could build a settlement, False if not

    >>> p_h, p_p, t_p = initiate_map('./data/init/')
    >>> hpl = list(set([sub_li[0] for sub_li in p_h]))
    >>> ttl = get_terrain_resource()
    >>> tnl = get_roll_num_list(ttl)
    >>> itd, td = generate_terrain_dict(ttl, tnl, t_p)
    >>> ptd, ppro, ppsl = point_terrain_creator(t_p, itd)

    >>> p = Player()
    >>> p.reachable_points = [55]
    >>> p.settlements = [0]
    >>> p.resource_list = [1, 1, 3, 1, 1]
    >>> hb1 = [0]
    >>> hb2 = [1]
    >>> rd = ResourceDict("road")
    >>> settlement_possible(p, hb1, p_p)
    False
    >>> settlement_possible(p, hb2, p_p)
    False
    """
    # check if possible brick, lumber, wool, grain num >= 1 each
    resources_list = player.resources_list
    # check if settlement number reaches the maximum requirement
    if len(player.settlements) == 5:
        return False
    # check if there has no place for building a settlement: all the reachable point cannot build a settlement
    reachable_points_lists = player.reachable_points.copy()

    building_neighbor = []
    for settlement_point in player.settlements:
        building_neighbor.extend(pp[settlement_point])
    for city_point in player.cities:
        building_neighbor.extend(pp[city_point])
    building_neighbor = list(set(building_neighbor))  # remove all redundant point

    buildable_point = []
    for point in reachable_points_lists:
        if (point not in player.settlements) and (point not in building_neighbor) and (point not in player.cities):
            buildable_point.append(point)

    if len(buildable_point) == 0:
        return False

    # check if resource is suitable without trading
    if (player.resources_list[0] >= 1) and (player.resources_list[1] >= 1) \
            and (player.resources_list[3] >= 1) and (player.resources_list[4] >= 1):
        return True
    # check if resource is suitable with trading
    trade_rate = get_trade_rate(player, harbor_point_list)

    resDic = ResourceDict("settlement")

    resource_lack, resource_turn = resource_compare_generator(player, trade_rate, resDic)

    return resource_lack <= resource_turn


def road_possible(player: Player, harbor_point_list):
    """
    Check if the current player could build a road
    :param player: Type Player
    :return: True if the player could build a road, False if not
    """
    # check if possible brick, lumber, wool, grain num >= 1 each
    resources_list = player.resources_list
    # check if settlement number reaches the maximum requirement
    if player.road_num == 15: return False
    # check if resource is suitable without trading
    if resources_list[0] >= 1 and resources_list[1] >= 1:
        return True

    # check if resource is suitable with trading
    trade_rate = get_trade_rate(player, harbor_point_list)

    resDic = ResourceDict("road")

    resource_lack, resource_turn = resource_compare_generator(player, trade_rate, resDic)

    return resource_lack <= resource_turn


def trade_supporter(player, trade_rate, resDic: ResourceDict):
    """
    Trade resource based on the needed action, trade every time it could trade
    :param player: player obejct
    :param trade_rate: 4 without harbor, else 3
    :param needed_dict: dict stores all needed function
    :param resource_list: list_stores all redundant resource idx for this building
    :param target_list: list stores all needed resource
    :return:
    >>> p = Player()
    >>> rd = ResourceDict("road")
    >>> p.resources_list = [1,0,3,0,0]
    >>> trade_supporter(p, 3, rd)
    >>> p.resources_list
    [1, 1, 0, 0, 0]
    >>> rd = ResourceDict("road")
    >>> p.resources_list = [1,0,3,0,0]
    >>> trade_supporter(p, 4, rd)
    >>> p.resources_list
    [1, 0, 3, 0, 0]
    >>> rd = ResourceDict("settlement")
    >>> p.resources_list = [1,0,3,1,1]
    >>> trade_supporter(p, 3, rd)
    >>> p.resources_list
    [1, 1, 0, 1, 1]
    >>> rd = ResourceDict("settlement")
    >>> p.resources_list = [1,0,3,1,1]
    >>> trade_supporter(p, 4, rd)
    >>> p.resources_list
    [1, 0, 3, 1, 1]
    >>> rd = ResourceDict("city")
    >>> p.resources_list = [3,0,2,2,0]
    >>> trade_supporter(p, 3, rd)
    >>> p.resources_list
    [0, 0, 3, 2, 0]
    >>> rd = ResourceDict("city")
    >>> p.resources_list = [3,0,2,2,0]
    >>> trade_supporter(p, 4, rd)
    >>> p.resources_list
    [3, 0, 2, 2, 0]
    """
    for need_id, need_num in resDic.needed_dict.items():
        if player.resources_list[need_id] < need_num:
            need_res = need_num - player.resources_list[need_id]
            for idx in resDic.resource_list:
                if need_res == 0:
                    continue
                cur_res = int(player.resources_list[idx] / trade_rate)
                trans_res = min(cur_res, need_res)
                player.resources_list[idx] -= trans_res * trade_rate
                player.resources_list[need_id] += trans_res
                need_res -= trans_res

            for idx in resDic.target_list:
                if need_res == 0:
                    continue
                if idx != need_id:
                    cur_res = int((player.resources_list[idx] - resDic.needed_dict[idx]) / trade_rate)
                    trans_res = min(cur_res, need_res)
                    player.resources_list[idx] -= trans_res * trade_rate
                    player.resources_list[need_id] += trans_res
                    need_res -= trans_res


def build_a_city(player, point_probability, harbor_point_list):
    """
    Upgrade a settlement into a city, can only run when can upgrade a city, would only choose the city with
        the highest probability to build
    :param player: Player
    :param point_probability: dict{point_idx: sum_roll}
    :return: void, player city and settlement list is change already
    """
    # trade if resource is not sufficient
    trade_rate = get_trade_rate(player, harbor_point_list)

    resDic = ResourceDict("city")

    trade_supporter(player, trade_rate, resDic)

    # build a city from current settlement which has the highest probability
    high_point, high_prob = player.settlements[0], point_probability[player.settlements[0]]
    for idx in range(1, len(player.settlements)):
        if high_prob < point_probability[player.settlements[idx]]:
            high_point = player.settlements[idx]
            high_prob = point_probability[player.settlements[idx]]

    player.settlements.remove(high_point)
    player.cities.append(high_point)
    player.resources_list[3] -= 2
    player.resources_list[2] -= 3
    player.vp += 1


def build_a_settlement(player, point_probability, pp, harbor_point_list):
    """
    Upgrade a settlement into a city, can only run when can upgrade a city, would only choose the city with
        the highest probability to build
    :param player: Player
    :param point_probability: dict{point_idx: sum_roll}
    :return: void, player city and settlement list is change already
    """
    # trade if resource is not sufficient
    trade_rate = get_trade_rate(player, harbor_point_list)

    resDic = ResourceDict("settlement")

    trade_supporter(player, trade_rate, resDic)

    # find all point that suitable for build a settlement
    # get all point with building
    building_points = player.settlements.copy()
    building_points.extend(player.cities)

    un_buildable_points = building_points.copy()
    for point in building_points:
        for neighbor_point in pp[point]:
            if (neighbor_point not in un_buildable_points) and (neighbor_point in player.reachable_points):
                un_buildable_points.append(neighbor_point)

    possible_point = player.reachable_points.copy()
    for point in un_buildable_points:
        if point in possible_point:
            possible_point.remove(point)

    # get all possible point from possible_point
    res_point, res_prob = possible_point[0], 0
    for point in possible_point:
        if (point not in un_buildable_points) and (point_probability[point] > res_prob):
            res_point = point
            res_prob = res_prob

    # build settlement in point
    for idx in resDic.target_list:
        player.resources_list[idx] -= 1
    player.settlements.append(res_point)
    player.vp += 1


def build_a_road(player, point_probability, pp, harbor_point_list, special_point=-1):
    """
    Build a road for current player
    :param player:
    :param point_probability:
    :param pp:
    :param harbor_point_list:
    :param special_point: special situation for origin creat , -1 in normal round
    :return:
    """
    if special_point == -1:
        # trade if resource is not sufficient
        trade_rate = get_trade_rate(player, harbor_point_list)

        resDic = ResourceDict("road")

        trade_supporter(player, trade_rate, resDic)

        # find all possible point for road building
        building_point = []

        # add all possible neighbors for player_reachable_points
        for reach_point in player.reachable_points:
            for nei_point in pp[reach_point]:
                if (nei_point not in player.settlements) and (nei_point not in player.cities) and (
                        nei_point not in player.reachable_points):
                    building_point.append(nei_point)

        target_point, target_prob = -1, -1
        # get the point with the highest probability
        for point in building_point:
            if point_probability[point] > target_prob:
                target_point = point
                target_prob = point_probability[point]

        # build the point in target point
        for idx in resDic.target_list:
            player.resources_list[idx] -= 1
        player.reachable_points.append(target_point)
        player.road_num += 1

    # default create point
    else:
        # find all possible point for current special point
        building_point = pp[special_point]

        target_point, target_prob = -1, -1
        # get the point with the highest probability
        for point in building_point:
            if point_probability[point] > target_prob:
                target_point = point
                target_prob_prob = point_probability[point]

        # since it is default, no resource created
        player.reachable_points.append(target_point)
        player.road_num += 1


def city_upgrade_prefer(player: Player, terrain_dict, point_probability, pp, harbor_point_list) -> None:
    """
    For Hypothesis 1, situation 1, upgrading a city when there has a settlement,
    building a settlement can only be considered if there does not have any settlement waiting for upgrading
    :param player:
    :param terrain_dict:
    :param point_probability:
    :param pp:
    :param harbor_point_list:
    """
    # building a settlement can only be considered if there does not have any settlement waiting for upgrading
    if len(player.settlements) == 0 or len(player.cities) == 4:
        trade_supporter(player, get_trade_rate(player, harbor_point_list), ResourceDict("settlement"))
        while settlement_possible(player, harbor_point_list, pp):
            build_a_settlement(player, point_probability, pp, harbor_point_list)
            # check if resource available for building a road + settlement: for loop * 2
        for _ in range(2):
            if road_possible(player, harbor_point_list):
                build_a_road(player, point_probability, pp, harbor_point_list)
            if settlement_possible(player, harbor_point_list, pp):
                build_a_settlement(player, point_probability, pp, harbor_point_list)

    trade_supporter(player, get_trade_rate(player, harbor_point_list), ResourceDict("city"))
    # check if resource available for upgrading a city: while loop
    while city_possible(player, harbor_point_list):
        build_a_city(player, point_probability, harbor_point_list)
        # check if resource available for building a settlement: while loop


def settlement_build_prefer(player: Player, terrain_dict, point_probability, pp, harbor_point_list) -> None:
    """
    For Hypothesis 1, situation 2, build a settlement is the first choice rather than upgrading a city,
    upgrading a city can only be considered if the settlement number reach 5
    :param player:
    :param terrain_dict:
    :param point_probability:
    :param pp:
    :param harbor_point_list:
    """
    # check if resource available for upgrading a city: while loop
    ## can only upgrade a city when all settlement is built, number of settlement reach 5
    if len(player.settlements) == 5 or player.road_num == 15:
        # two possible situation to consider upgrade to a city:
        #     1. the settlement reaches highest demands
        #     2. no more road to build, but have settlement ungraded
        trade_supporter(player, get_trade_rate(player, harbor_point_list), ResourceDict("city"))
        while city_possible(player, harbor_point_list):
            build_a_city(player, point_probability, harbor_point_list)
            # check if resource available for building a settlement: while loop

    trade_supporter(player, get_trade_rate(player, harbor_point_list), ResourceDict("settlement"))
    while settlement_possible(player, harbor_point_list, pp):
        build_a_settlement(player, point_probability, pp, harbor_point_list)
        # check if resource available for building a road + settlement: for loop * 2
    for _ in range(2):
        if road_possible(player, harbor_point_list):
            build_a_road(player, point_probability, pp, harbor_point_list)
        if settlement_possible(player, harbor_point_list, pp):
            build_a_settlement(player, point_probability, pp, harbor_point_list)


def harbor_build_prefer(player: Player, terrain_dict, point_probability, pp, harbor_point_list, harbor_path,
                        dest_harbor) -> None:
    """
    For Hypothesis 2, situation 2, build a settlement in a harbor city first if there does not have any harbor city yet
    :param player:
    :param terrain_dict:
    :param point_probability:
    :param pp:
    :param harbor_point_list:
    """
    # step 1: build road to latest harbor first if the player does not have harbor settlement yet
    building_point_list = player.cities.copy()
    building_point_list.extend(player.settlements)

    # check whether player owns a harbor
    if own_harbor(player, harbor_point_list) or (len(harbor_path) == 0) or (len(harbor_path) > 6) or (
            len(harbor_path) < (15 - player.road_num)):
        # step 2: if already have a harbor, do as settlement first
        settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    else:
        # build road to the nearest harbor until it build a settlement in harbor
        trade_supporter(player, get_trade_rate(player, harbor_point_list), ResourceDict("road"))
        while road_possible(player, harbor_point_list) and len(harbor_path) > 0:
            # road is buildable and the harbor point is reachable
            cur_road = harbor_path.pop(0)
            cur_reachable = player.reachable_points.copy()
            cur_reachable.append(cur_road)
            build_a_road(player, point_probability, pp, harbor_point_list)
            player.reachable_points = cur_reachable
        # check if the harbor has a building, if not, try build a building
        if settlement_possible(player, harbor_point_list, pp):
            cur_settlements = player.settlements.copy()
            cur_settlements.append(dest_harbor)
            build_a_settlement(player, point_probability, pp, harbor_point_list)
            player.settlements = cur_settlements


def shortest_harbor_path(cur_settlements: list, reachable_list: list, pp, harbor_point_list: list,
                         player_list: list) -> [int, list]:
    """
    get the nearest point(harbor) to the point and the shortest path to the point
    :param player:
    :param pp:
    :param harbor_point_list:
    :return: int represent the point contians the harbor, list contians the road to build the path
    """
    harbor_point = 0
    res_list = [*range(0, 54, 1)]

    # remove all valid harbor_point_list if they are the neighbor for current player
    cur_harbor_point_list = harbor_point_list.copy()
    building_points = []

    # add all other player settlement and city into cur_settlements:
    for p in player_list:
        settlements = p.settlements.copy()
        cities = p.cities.copy()
        for settlement in settlements:
            if settlement not in cur_settlements:
                building_points.append(settlement)
                cur_settlements.append(settlement)
        for city in cities:
            if city not in cur_settlements:
                building_points.append(city)
                cur_settlements.append(city)

    for settlement in cur_settlements:
        neighbors = pp[settlement]
        for nei in neighbors:
            if nei in cur_harbor_point_list:
                cur_harbor_point_list = [ele for ele in cur_harbor_point_list if ele != nei]

    for start_point in reachable_list:
        cur_path = find_shortest_path(start_point, pp, cur_harbor_point_list, building_points)

        if len(cur_path) < len(res_list):
            res_list = cur_path
            harbor_point = res_list[len(res_list) - 1]

    return harbor_point, res_list


def find_shortest_path(start_point: int, pp: list, harbor_point_list: list, building_points: list) -> list:
    """
    Support function to find the shortest path start from start_point, Using BFS
    Idea from:
        Wikipedia contributors. “Breadth-first Search.” Wikipedia, 27 Feb. 2023, en.wikipedia.org/wiki/Breadth-first_search.

    :param start_point: the start point for the path, default will not be the harbor_point_list
    :param pp: point-point list
    :param harbor_point_list: list contains all possible harbor result
    :param cur_path: list for all current visited path
    :param res_list: return current best route
    :return: int represent the point contains the harbor, list contains the road to build the path
    """
    queue_list = [[start_point]]
    visited = [start_point]
    if start_point in harbor_point_list:
        return [start_point]

    while len(queue_list) > 0:
        size = len(queue_list)
        new_layer = []
        for _ in range(size):
            cur_route = queue_list.pop(0)
            cur_point = cur_route[-1]
            if cur_point in harbor_point_list:
                return cur_route
            neighbors = pp[cur_point]
            for neighbor in neighbors:
                route = cur_route.copy()
                if neighbor not in cur_route:
                    route.append(neighbor)
                    if neighbor not in visited:
                        new_layer.append(neighbor)
                    queue_list.append(route)
        visited.extend(new_layer)

    return []


def get_resource(player_list: list, terrain_dict: dict, dice_num: int) -> None:
    """
        Simulatte the resource get process, after the function, all resources were updated
    :param player:
    :param terrain_dict:
    :return:
    """
    # dice_num = roll_dice() + roll_dice()
    terrain_resources = [[t.point, t.resource] for t in terrain_dict[dice_num]]

    ## step 2: find all player owned place, add resource
    # add 1 resouce to all settlments
    for player in player_list:
        player_buildings = player.settlements
        if dice_num != 7:  # if the number is 7, do not have any resource, jump out for further report
            for building_point in player_buildings:
                for [des_point_list, point_resource] in terrain_resources:
                    player.resources_list[point_resource] += 1 if building_point in des_point_list else 0

            player_buildings = player.cities
            for building_point in player_buildings:
                for [des_point_list, point_resource] in terrain_resources:
                    player.resources_list[point_resource] += 2 if building_point in des_point_list else 0
        else:  # dice_num == 7
            # if the dice rolls 7, player must discard resources if the resources number larger than 7
            # hypothesis: player always discard the most resources type
            discard_num = sum(player.resources_list) // 2 if sum(player.resources_list) > 7 else 0
            while discard_num > 0:
                player.discard_one_resource()
                discard_num -= 1


def get_rec_list(player: Player):
    """
    Create record list for potential analysis
    :param player:
    :return:
    """
    vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = [], [], [], [], [], [], [], [], []
    vp_rec.append(player.vp)
    set_rec.append(len(player.settlements))
    city_rec.append(len(player.cities))
    road_rec.append(player.road_num)
    brick_rec.append(player.resources_list[0])
    lum_rec.append(player.resources_list[1])
    ore_rec.append(player.resources_list[2])
    grain_rec.append(player.resources_list[3])
    wool_rec.append(player.resources_list[4])
    return RecordList(vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec)


def check_game_pass(player, time, vp, epoch, max_round):
    """
    Check whether the player wins the game, display the current situation for player if the round reaches a check point
    :param player: Player object
    :param time: current round number start with 0
    :param vp: setting victory point
    :param epoch: check whether a display is needed
    :param max_round: max round for each point
    :return: True if player wins game, False if not or exceed final loop
    >>> time, vp, epoch, max_round = 100, 8, 51, 200
    >>> p = Player()
    >>> p.vp = 7
    >>> check_game_pass(p, time, vp, epoch, max_round)
    False
    """
    if player.vp >= vp:
        print("==============================")
        print(f"game finished, player win in round {time + 1}")
        print("Player status display:")
        player.print_player()
        return True
    # if not, check player situation for every 50 rounds
    # if (time + 1) % epoch == 0:
    #     print("==============================")
    #     print(f"player status after round {time + 1}")
    #     print("Player status display:")
    #     player.print_player()

    if time == max_round - 1:
        print("==============================")
        print("game over, player failed to reach victory point")

    return False


def simulation_process(player, terrain_dict, point_probability, pp, harbor_point_list, strategy, time,
                       player_list: list, max_round=200, vp=10,
                       epoch=50):
    """

    :param player:
    :param terrain_dict:
    :param point_probability:
    :param pp:
    :param harbor_point_list:
    :param strategy_Function: 1 for settlement, 2 for city, 3 for harbor
    :param max_round:
    :param vp:
    :param epoch:
    :return:
    """
    if strategy == "harbor_prefer":
        settlements = player.settlements.copy()
        settlements.extend(player.cities.copy())

        dest_harbor_point, dest_path = shortest_harbor_path(player.settlements, player.reachable_points, pp,
                                                            harbor_point_list, player_list)
    ## for settlement prefer strategy
    max_round, vp, gamePass = max_round, vp, False
    reclist = get_rec_list(player)
    used_round = time
    # for time in range(max_round):
    # step 1: get resource
    # get_resource(player, terrain_dict)
    # step 2: check for any possible build process
    if strategy == "settlement_prefer":
        settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    elif strategy == "city_prefer":
        city_upgrade_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    elif strategy == "harbor_prefer":
        harbor_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list, dest_path,
                            dest_harbor_point)
    # step 3: store current status into resource recorder for later display
    reclist = get_rec_list(player)
    # step 4: check if player wins, if so, display and return all results
    gamePass = check_game_pass(player, time, vp, epoch, max_round)
    resRecoder = ResRecoder(used_round, gamePass)
    return resRecoder, reclist


def vis_two_round(round_rec1: list, round_rec2: list, round1_type: str, round2_type: str, hypo: int, compete: False,
                  simulation_times=1000):
    """
    Create plot for number store
    :param round_rec1:
    :param round_rec2:
    :param round1_type:
    :param round2_type:
    :param hypo:
    :param simulation_times:
    :return:
    """
    if len(round_rec1) < simulation_times:
        for _ in range(simulation_times - len(round_rec1)):
            round_rec1.append(0)
    if len(round_rec2) < simulation_times:
        for _ in range(simulation_times - len(round_rec2)):
            round_rec2.append(0)

    # visualization
    x_val = [*range(simulation_times)]
    y_rec1 = round_rec1
    y_rec2 = round_rec2

    title = f"Vis_for_Hypothesis_{hypo}"

    plt.title(title)
    plt.xlabel("Times")
    plt.ylabel("Used Rounds")
    plt.plot(x_val, y_rec1)
    plt.plot(x_val, y_rec2)
    plt.legend([round1_type, round2_type])
    output_name = './data/output/' + title
    if compete:
        output_name += '_Compete'
    plt.savefig(output_name)
    plt.close()

    mean1 = sum(y_rec1) / len(y_rec1)
    mean2 = sum(y_rec2) / len(y_rec2)

    title = f"Statistic_Vis_for_Hypothesis_{hypo}"
    bins = np.linspace(0, max_round, max_round // 10)
    plt.xlabel("Times")
    plt.ylabel("Used Rounds")
    plt.hist(y_rec1, bins, alpha=0.5)
    plt.axvline(x=mean1, color='blue', linestyle='-', alpha=0.5)
    plt.hist(y_rec2, bins, alpha=0.5)
    plt.axvline(x=mean2, color='orange', linestyle='-', alpha=0.5)
    plt.legend([round1_type, round2_type])
    output_name = './data/output/' + title
    if compete:
        output_name += '_Compete'
    plt.savefig(output_name)
    plt.close()

    bar_vis(round_rec1, round_rec2, round1_type, round2_type, compete)


def board_save(point_terrain_dict: dict, idx_terrain_dict: dict, filename: str) -> None:
    """
    Save the current board situation into a csv file
    :param point_terrain_dict:
    :return: an output csv file stores the current board situation
    """
    # default setting
    header = [["Resource"]]
    for i in range(2, 13, 1):
        header[0].append(i)
    resource_list = [["Brick"], ["Lumber"], ["Ore"], ["Grain"], ["Wool"]]
    for resource in resource_list:
        for i in range(2, 13, 1):
            resource.append(0)
    # add number into resources
    for point, terrains in point_terrain_dict.items():
        for terrainidx in terrains:
            terrain = idx_terrain_dict[terrainidx]
            if terrain.resource == 5: continue  # find dessert
            resource_list[terrain.resource][terrain.num - 1] += 1

    for resourceli in resource_list:
        header.append(resourceli)

    # display resource situation
    # print(header)
    # for resource in resource_list:
    #     print(resource)

    # stroe situation into a csvfile
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=',')
        writer.writerows(header)


def dice_visualization(num_list, compete=True):
    """
    Visualize the distribution of rolling 2 dices
    :param num_list:
    :return:
    """
    x_val = [*range(2, 13, 1)]
    plt.bar(x_val, num_list)
    plt.ylabel("Roll times")
    plt.xlabel("Roll Value")
    title = "Dice_visualization"
    output_name = './data/output/' + title
    if compete:
        output_name += '_Compete'
    plt.savefig(output_name)
    plt.close()


def bar_vis(val1: list, val2: list, name1, name2, compete=False):
    res = [0, 0, 0]
    for i in range(len(val1)):
        if val1[i] < val2[i]:
            res[0] += 1
        elif val1[i] > val2[i]:
            res[1] += 1
        else:
            res[2] += 1

    title = "pie_" + name1 + "_" + name2
    plt.pie(res, labels=[name1, name2, "draw"])
    output_name = './data/output/' + title
    if compete:
        output_name += '_Compete'
    plt.legend([name1, name2, "draw"])
    plt.savefig(output_name)
    plt.close()


if __name__ == '__main__':
    """
    Variable for all used data structures
        ph: point - harbor list [[point, harboridx, harbor_type, harbor_resource]], represent point has harbor
            harbaor_type:
                2: universal
                1: special for 2: 1, harbor_resource reflect the number
        pp: point - point list [[point list]], represent point idx as point list as adjacent 
        tp: terrain - point list [[terrain, point]], represent terrain was surrounded by points 
        terrain_type_list: list with length: terrain number, each number represents the source in this terrain 
            resource list:
            5 -> dessert, create nothing 
            0 -> hills, create brick
            1 -> forest, create lumber
            2 -> mountains, create ore
            3 -> fields, create grain
            4 -> pasture, create wool
        terrain_number_list: list with roll numbers, each number represents the roll number of each terrain
            7 means dessert 
        idx_terrain_dict: dict{terrain idx: terrain element}, each terrain element has a unique terrain index
        terrain_dict: dict{number: terrain element}, roll a number means the all related terrains would get resources
        point_terrain_dict: dict{point_idx: list[ terrain_idx ]}, a point has terrain
        point_probability: dict{point_idx: sum_roll}, the probability of each point that might get number
        point_probability_sort_list: list [ point idx ], the order represent the probability of each point that might roll the number 
        pp_dict: {point, [points_neighbor]}, all point with their neighbors
        harbor_point_list: [points], shows all points that owns a harbor 
    """

    # visualize dice rolling distribution
    test = [0] * 11
    for _ in range(100000):
        test[roll_dice() + roll_dice() - 2] += 1
    dice_visualization(test, compete=True)

    init_data_url = './data/init/'
    # test for initiate map
    ph, pp, tp = initiate_map(init_data_url)
    harbor_point_list = list(set([sub_li[0] for sub_li in ph]))
    terrain_type_list = get_terrain_resource()
    terrain_number_list = get_roll_num_list(terrain_type_list)
    idx_terrain_dict, terrain_dict = generate_terrain_dict(terrain_type_list, terrain_number_list, tp)
    point_terrain_dict, point_probability, point_probability_sort_list = point_terrain_creator(tp, idx_terrain_dict)

    ## store the current board situation
    board_save(point_terrain_dict, idx_terrain_dict, 'data/output/border.csv')

    ## simulation part
    simulation_times, max_round, vp, epoch = 1000, 400, 10, 50
    val1 = []
    val2 = []
    val3 = []

    strategy_list = ["settlement_prefer", "city_prefer"]
    res_dict = {}
    for strategy in strategy_list:
        res_dict[strategy] = []

    # for i in range(simulation_times):
    #     # create a new board and save
    #     print("=====================")
    #     print(f"{i} times simulation:")
    #     harbor_point_list = list(set([sub_li[0] for sub_li in ph]))
    #     terrain_type_list = get_terrain_resource()
    #     terrain_number_list = get_roll_num_list(terrain_type_list)
    #     idx_terrain_dict, terrain_dict = generate_terrain_dict(terrain_type_list, terrain_number_list, tp)
    #     point_terrain_dict, point_probability, point_probability_sort_list = point_terrain_creator(tp, idx_terrain_dict)
    #     filename = 'data/border/border' + str(i) + '.csv'
    #     board_save(point_terrain_dict, idx_terrain_dict, filename)
    #
    #     finishcnt = 0
    #     player_li = compete_player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
    #                                          point_probability, strategy_list)
    #
    #     for times in range(max_round):
    #         if finishcnt == len(player_li):
    #             break
    #         # each player start their round
    #         for player in player_li:
    #             if player.vp < vp:
    #                 dice_num = roll_dice() + roll_dice()
    #                 # All player get resource:
    #                 get_resource(player_li, terrain_dict, dice_num)
    #                 # action for this player
    #                 resRecoder, reclist = simulation_process(player, terrain_dict, point_probability, pp, harbor_point_list, player.strategy, times, player_li,
    #                                    max_round=max_round, vp=vp, epoch=epoch)
    #                 if player.vp >= vp or (times == (max_round - 1)):
    #                     curli = res_dict[player.strategy]
    #                     print(curli)
    #                     curli.append(times + 1)
    #                     res_dict[player.strategy] = curli
    #                     print(f"{player.strategy}: {times + 1}")
    #                     finishcnt += 1
    #         # Each player start their turn
    #
    # print(res_dict)
    # val1 = []
    # val2 = []
    # for idx, lis in res_dict.items():
    #     if idx == "settlement_prefer":
    #         val1 = lis
    #     else:
    #         val2 = lis
    #
    # vis_two_round(val1, val2, "settlement prefer", "city prefer", 1, simulation_times=simulation_times, compete=True)

    strategy_list = ["harbor_prefer", "city_prefer"]
    res_dict = {}
    for strategy in strategy_list:
        res_dict[strategy] = []

    for i in range(simulation_times):
        # create a new board and save
        print("=====================")
        print(f"{i} times simulation:")
        harbor_point_list = list(set([sub_li[0] for sub_li in ph]))
        terrain_type_list = get_terrain_resource()
        terrain_number_list = get_roll_num_list(terrain_type_list)
        idx_terrain_dict, terrain_dict = generate_terrain_dict(terrain_type_list, terrain_number_list, tp)
        point_terrain_dict, point_probability, point_probability_sort_list = point_terrain_creator(tp, idx_terrain_dict)
        filename = 'data/border/border' + str(i) + '.csv'
        board_save(point_terrain_dict, idx_terrain_dict, filename)

        finishcnt = 0
        player_li = compete_player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                             point_probability, strategy_list)

        for times in range(max_round):
            if finishcnt == len(player_li):
                break
            # each player start their round
            for player in player_li:
                if player.vp < vp:
                    dice_num = roll_dice() + roll_dice()
                    # All player get resource:
                    get_resource(player_li, terrain_dict, dice_num)
                    # action for this player
                    resRecoder, reclist = simulation_process(player, terrain_dict, point_probability, pp,
                                                             harbor_point_list, player.strategy, times, player_li,
                                                             max_round=max_round, vp=vp, epoch=epoch)
                    if player.vp >= vp or (times == (max_round - 1)):
                        curli = res_dict[player.strategy]
                        print(curli)
                        curli.append(times + 1)
                        res_dict[player.strategy] = curli
                        print(f"{player.strategy}: {times + 1}")
                        finishcnt += 1
            # Each player start their turn

    print(res_dict)
    val1 = []
    val2 = []
    for idx, lis in res_dict.items():
        if idx == "city_prefer":
            val2 = lis
        else:
            val1 = lis

    vis_two_round(val1, val2, "harbor prefer", "city prefer", 2, simulation_times=simulation_times, compete=True)
