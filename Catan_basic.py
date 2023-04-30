import random
import pandas as pd
from Elements import Player, Terrain, Point
import matplotlib.pyplot as plt


def roll_dice() -> int:
    """
    Rolling a dice, would return random number between 1 - 6
    :return: Integer between 1 - 6
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


def simulation(player: Player, resourcelist: dict, target_point=10):
    # simulate a round process
    if player.vp == target_point:
        # if it reaches vp point, just return the point and return
        raise NotImplemented
    else:
        # start running simulation
        num = roll_dice() + roll_dice()


def get_terrain_resource():
    """
    Designate resource to each terrain in random
    :return: A list of resource type of each terrain
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
    # create a dict for resource sufficient using tp
    point_terrain_dict = {}
    for terrain_id in range(len(tp)):
        for point_id in tp[terrain_id]:
            point_terrain_dict.setdefault(point_id, []).append(terrain_id)
    # print(point_terrain_dict)
    num_pro_list = [0, 0, 1, 2, 3, 4, 5, 0, 5, 4, 3, 2, 1]
    # calculate the possibility of each point
    point_probability = {}
    for point, terrains in point_terrain_dict.items():
        probability = 0
        for terrain_idx in terrains:
            ter_num = idx_terrain_dict[terrain_idx].num
            probability += num_pro_list[ter_num]
        point_probability[point] = probability
    # print(point_probability)
    # sort the point_probability dict
    point_probability_sort_list = sorted(point_probability, key=point_probability.get, reverse=True)
    # print(point_probability_sort_list)
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
    # remove all unreachable points
    # for point in point_list:
    #     # if point in un_buildable_list:
    #     #     un_buildable_list.remove(point)
    #     unreachable_points = pp[point]
    #     for near_point in unreachable_points:
    #         if near_point in buildable_list:
    #             buildable_list.remove(near_point)
    return point2 not in not_buildable_list


def player_generater(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict, point_probability):
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
    # print("resources")
    # for terrain_idx in terrain_list:
    #     cur_terrain_res = idx_terrain_dict[terrain_idx].resource
    #     print(cur_terrain_res)
    #     player.resources_list[cur_terrain_res] += 1

    # build 2 roads for current place
    build_a_road(player, point_probability, pp, harbor_point_list, special_point=point_probability_sort_list[0])
    build_a_road(player, point_probability, pp, harbor_point_list, special_point=point_probability_sort_list[point2])

    player.vp = 2
    player.road_num = 2
    print('player setting created, bellowed is the original situation ')
    player.print_player()
    return player


def simulation_single_round(player: Player, pp, tp, ph, terrain_type_list, idx_terrain_dict, point_terrain_dict,
                            simulation_times=1000):
    return 0


def own_harbor(player, harbor_point_list):
    possible_point = player.settlements.copy()
    possible_point.extend(player.cities)
    for point in possible_point:
        if point in harbor_point_list:
            return True
    return False


def city_possible(player: Player, harbor_point_list):
    """
    Check if the current player could build a city
    :param player: Type Player
    :return: True if the player could build a city, False if not
    """
    # check if possible grain num >= 2 and ore num >= 3
    resources_list = player.resources_list
    # check if there has settlements for upgrading
    if len(player.settlements) == 0 or len(player.cities) == 4: return False
    # check if resource is suitable without trading
    if resources_list[2] >= 3 and resources_list[3] >= 2: return True

    # check if resource is suitable with trading
    trade_rate = 3 if own_harbor(player, harbor_point_list) else 4
    needed_dict = {2: 3, 3: 2}
    resource_list = [0, 1, 4]
    target_list = [2, 3]

    resource_lack = 0
    resource_turn = 0 # source could get via trading

    for idx in range(5):
        # check if the needed resource is redundant
        if idx in target_list:
            if needed_dict[idx] < player.resources_list[idx]:
                resource_turn += int(max(player.resources_list[idx] - needed_dict[idx], 0) / trade_rate)
            else:
                resource_lack += max(needed_dict[idx] - player.resources_list[idx], 0)
        else:
            resource_turn += int(max(player.resources_list[idx], 0) / trade_rate)

    return resource_lack <= resource_turn


def settlement_possible(player: Player, harbor_point_list, pp):
    """
    Check if the current player could build a settlement
    :param player: Type Player
    :return: True if the player could build a settlement, False if not
    """
    # check if possible brick, lumber, wool, grain num >= 1 each
    resources_list = player.resources_list
    # check if settlement number reaches the maximum requirement
    if len(player.settlements) == 5: return False
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
        if point not in player.settlements and point not in building_neighbor and point not in player.cities:
            buildable_point.append(point)

    if len(buildable_point) == 0: return False

    # check if resource is suitable without trading
    if resources_list[0] >= 1 and resources_list[1] >= 1 and resources_list[3] >= 1 and resources_list[4] >= 1:
        return True
    # check if resource is suitable with trading
    trade_rate = 3 if own_harbor(player, harbor_point_list) else 4
    needed_dict = {0: 1, 1: 1, 3: 1, 4: 1}
    resource_list = [2]
    target_list = [0, 1, 3, 4]

    resource_lack = 0
    resource_turn = 0

    for idx in range(5):
        # check if the needed resource is redundant
        if idx in target_list:
            resource_lack += max(needed_dict[idx] - player.resources_list[idx], 0)
            resource_turn += int(max(player.resources_list[idx] - needed_dict[idx], 0) / trade_rate)
        else:
            resource_turn += int(max(player.resources_list[idx], 0) / trade_rate)

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
    trade_rate = 3 if own_harbor(player, harbor_point_list) else 4
    needed_dict = {0: 1, 1: 1}
    resource_list = [2, 3, 4]
    target_list = [0, 1]

    resource_lack = 0
    resource_turn = 0

    for idx in range(5):
        # check if the needed resource is redundant
        if idx in target_list:
            resource_lack += max(needed_dict[idx] - player.resources_list[idx], 0)
            resource_turn += int(max(player.resources_list[idx] - needed_dict[idx], 0) / trade_rate)
        else:
            resource_turn += int(max(player.resources_list[idx], 0) / trade_rate)

    return resource_lack <= resource_turn


def build_a_city(player, point_probability, harbor_point_list):
    """
    Upgrade a settlement into a city, can only run when can upgrade a city, would only choose the city with
        the highest probability to build
    :param player: Player
    :param point_probability: dict{point_idx: sum_roll}
    :return: void, player city and settlement list is change already
    """
    # trade if resource is not sufficient
    trade_rate = 3 if own_harbor(player, harbor_point_list) else 4
    needed_dict = {2: 3, 3: 2}
    resource_list = [0, 1, 4]
    target_list = [2, 3]

    for need_id, need_num in needed_dict.items():
        if player.resources_list[need_id] < need_num:
            need_res = need_num - player.resources_list[need_id]
            for idx in resource_list:
                if need_res == 0:
                    continue
                cur_res = int(player.resources_list[idx] / trade_rate)
                trans_res = min(cur_res, need_res)
                player.resources_list[idx] -= trans_res * trade_rate
                player.resources_list[need_id] += trans_res
                need_res -= trans_res

            for idx in target_list:
                if need_res == 0:
                    continue
                if idx != need_id:
                    cur_res = int((player.resources_list[idx] - needed_dict[idx]) / trade_rate)
                    trans_res = min(cur_res, need_res)
                    player.resources_list[idx] -= trans_res * trade_rate
                    player.resources_list[need_id] += trans_res
                    need_res -= trans_res

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
    trade_rate = 3 if own_harbor(player, harbor_point_list) else 4
    needed_dict = {0: 1, 1: 1, 3: 1, 4: 1}
    resource_list = [2]
    target_list = [0, 1, 3, 4]

    for need_id, need_num in needed_dict.items():
        if player.resources_list[need_id] < need_num:
            need_res = need_num - player.resources_list[need_id]
            for idx in resource_list:
                if need_res == 0:
                    continue
                cur_res = int(player.resources_list[idx] / trade_rate)
                trans_res = min(cur_res, need_res)
                player.resources_list[idx] -= trans_res * trade_rate
                player.resources_list[need_id] += trans_res
                need_res -= trans_res

            for idx in target_list:
                if need_res == 0:
                    continue
                if idx != need_id:
                    cur_res = int((player.resources_list[idx] - needed_dict[idx]) / trade_rate)
                    trans_res = min(cur_res, need_res)
                    player.resources_list[idx] -= trans_res * trade_rate
                    player.resources_list[need_id] += trans_res
                    need_res -= trans_res

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
    # print(f"Cuurent possible point list: {possible_point}, len: {len(possible_point)}")
    res_point, res_prob = possible_point[0], 0
    for point in possible_point:
        if (point not in un_buildable_points) and (point_probability[point] > res_prob):
            res_point = point
            res_prob = res_prob

    # build settlement in point
    for idx in target_list:
        player.resources_list[idx] -= 1
    player.settlements.append(res_point)
    player.vp += 1


def build_a_road(player, point_probability, pp, harbor_point_list, special_point=-1):
    """

    :param player:
    :param point_probability:
    :param pp:
    :param harbor_point_list:
    :param special_point: special situation for origin creat , -1 in normal round
    :return:
    """
    if special_point == -1:
        # trade if resource is not sufficient
        trade_rate = 3 if own_harbor(player, harbor_point_list) else 4
        needed_dict = {0: 1, 1: 1}
        resource_list = [2, 3, 4]
        target_list = [0, 1]

        for need_id, need_num in needed_dict.items():
            if player.resources_list[need_id] < need_num:
                need_res = need_num - player.resources_list[need_id]
                for idx in resource_list:
                    if need_res == 0:
                        continue
                    cur_res = int(player.resources_list[idx] / trade_rate)
                    trans_res = min(cur_res, need_res)
                    player.resources_list[idx] -= trans_res * trade_rate
                    player.resources_list[need_id] += trans_res
                    need_res -= trans_res

                for idx in target_list:
                    if need_res == 0:
                        continue
                    if idx != need_id:
                        cur_res = int((player.resources_list[idx] - needed_dict[idx]) / trade_rate)
                        trans_res = min(cur_res, need_res)
                        player.resources_list[idx] -= trans_res * trade_rate
                        player.resources_list[need_id] += trans_res
                        need_res -= trans_res

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
        for idx in target_list:
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
    # h1: situation 1: if there has a settlment, then upgrade the city
    # prerequest1: player would upgrade the city with highest probability

    # check if resource available for upgrading a city: while loop
    while city_possible(player, harbor_point_list):
        build_a_city(player, point_probability, harbor_point_list)
        # check if resource available for building a settlement: while loop
    # building a settlement can only be considered if there does not have any settlement waiting for upgrading
    if len(player.settlements) == 0 or len(player.cities) == 4:
        while settlement_possible(player, harbor_point_list, pp):
            # print("settlement_build_prefer() pass")
            build_a_settlement(player, point_probability, pp, harbor_point_list)
            # check if resource available for building a road + settlement: for loop * 2
        for _ in range(2):
            if road_possible(player, harbor_point_list):
                build_a_road(player, point_probability, pp, harbor_point_list)
            if settlement_possible(player, harbor_point_list, pp):
                build_a_settlement(player, point_probability, pp, harbor_point_list)


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
    # h1: situation 1: if there has a settlment, then upgrade the city
    # prerequest1: player would upgrade the city with highest probability

    ## step3: check if the resource is suitable for building
    ## h1, situation 1, first check whether upgrading city is possible

    # check if resource available for upgrading a city: while loop
    ## can only upgrade a city when all settlement is built, number of settlement reach 5
    if len(player.settlements) == 5 or player.road_num == 15:
        # two possible situation to consider upgrade to a city:
        #     1. the settlement reaches highest demands
        #     2. no more road to build, but have settlement ungraded
        while city_possible(player, harbor_point_list):
            build_a_city(player, point_probability, harbor_point_list)
            # check if resource available for building a settlement: while loop

    # while road_possible(player, harbor_point_list):
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
    if own_harbor(player, harbor_point_list):
        # step 2: if already have a harbor, do as settlement first
        settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    else:
        # build road to the nearest harbor until it build a settlement in harbor
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


def shortest_harbor_path(cur_settlements: list, reachable_list: list, pp, harbor_point_list: list) -> [int, list]:
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
    for settlement in cur_settlements:
        neighbors = pp[settlement]
        for nei in neighbors:
            if nei in cur_harbor_point_list:
                cur_harbor_point_list = [ele for ele in cur_harbor_point_list if ele != nei]

    for start_point in reachable_list:
        cur_path = find_shortest_path(start_point, pp, cur_harbor_point_list)

        if len(cur_path) < len(res_list):
            res_list = cur_path
            harbor_point = res_list[len(res_list) - 1]

    return harbor_point, res_list


def find_shortest_path(start_point: int, pp: list, harbor_point_list: list) -> list:
    """
    Support function to find the shortest path start from start_point, Using BFS
    :param start_point: the start point for the path, default will not be the harbor_point_list
    :param pp: point-point list
    :param harbor_point_list: list contains all possible result
    :param cur_path: list for all current visited path
    :param res_list: return current best route
    :return: int represent the point contains the harbor, list contains the road to build the path
    """
    queue_list = [[start_point]]
    visited = [start_point]
    if start_point in harbor_point_list:
        # if len(cur_path) <= len(cur_res_list):
        return [start_point]

    while queue_list is not None:
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

    return None


def get_resource(player: Player, terrain_dict: dict) -> None:
    """
        Simulatte the resource get process, after the function, all resources were updated
    :param player:
    :param terrain_dict:
    :return:
    """
    dice_num = roll_dice() + roll_dice()
    terrain_resources = [[t.point, t.resource] for t in terrain_dict[dice_num]]

    ## step 2: find all player owned place, add resource
    # add 1 resouce to all settlments
    player_buildings = player.settlements
    if dice_num != 7:  # if the number is 7, do not have any resource, jump out for further report
        for building_point in player_buildings:
            for [des_point_list, point_resource] in terrain_resources:
                player.resources_list[point_resource] += 1 if building_point in des_point_list else 0

        player_buildings = player.cities
        for building_point in player_buildings:
            for [des_point_list, point_resource] in terrain_resources:
                player.resources_list[point_resource] += 2 if building_point in des_point_list else 0


def get_rec_list(player: Player):
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
    return vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec


def check_game_pass(player, time, vp, epoch, max_round):
    if player.vp >= vp:
        print("==============================")
        print(f"game finished, player win in round {time + 1}")
        print("Player status display:")
        player.print_player()
        return True
    # if not, check player situation for every 50 rounds
    if (time + 1) % epoch == 0:
        print("==============================")
        print(f"player status after round {time + 1}")
        print("Player status display:")
        player.print_player()

    if time == max_round - 1:
        print("==============================")
        print("game over, player failed to reach victory point")

    return False


def settlement_simulation(player, terrain_dict, point_probability, pp, harbor_point_list, max_round=200, vp=10,
                          epoch=50):
    ## for settlement prefer strategy
    max_round, vp, gamePass = max_round, vp, False
    vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = get_rec_list(player)
    used_round = max_round
    for time in range(max_round):
        # step 1: get resource
        get_resource(player, terrain_dict)
        # step 2: check for any possible build process
        settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)

        # step 3: store current status into resource recorder for later display
        vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = get_rec_list(player)

        # step 4: check if player wins, if so, display and return all results
        gamePass = check_game_pass(player, time, vp, epoch, max_round)
        if gamePass:
            used_round = time
            break

    return used_round, gamePass, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec


def city_simulation(player, terrain_dict, point_probability, pp, harbor_point_list, max_round=200, vp=10,
                    epoch=50):
    ## for settlement prefer strategy
    max_round, vp, gamePass = max_round, vp, False
    vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = get_rec_list(player)
    used_round = max_round

    for time in range(max_round):
        # step 1: get resource
        get_resource(player, terrain_dict)
        # step 2: check for any possible build process
        city_upgrade_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)

        # step 3: store current status into resource recorder for later display
        vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = get_rec_list(player)

        # step 4: check if player wins, if so, display and return all results
        gamePass = check_game_pass(player, time, vp, epoch, max_round)
        if gamePass:
            used_round = time
            break

    return used_round, gamePass, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec


def harbor_simulation(player, terrain_dict, point_probability, pp, harbor_point_list, max_round=200, vp=10,
                      epoch=50):
    ## for settlement prefer strategy
    dest_harbor_point, dest_path = shortest_harbor_path(player.settlements, player.reachable_points, pp,
                                                        harbor_point_list)

    max_round, vp, gamePass = max_round, vp, False
    vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = get_rec_list(player)
    used_round = max_round
    for time in range(max_round):
        # step 1: get resource
        get_resource(player, terrain_dict)
        # step 2: check for any possible build process
        harbor_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list, dest_path,
                            dest_harbor_point)

        # step 3: store current status into resource recorder for later display
        vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = get_rec_list(player)

        # step 4: check if player wins, if so, display and return all results
        gamePass = check_game_pass(player, time, vp, epoch, max_round)
        if gamePass:
            used_round = time
            break

    return used_round, gamePass, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec


def vis_two_round(round_rec1: list, round_rec2: list, round1_type: str, round2_type: str, hypo: int,
                  simulation_times=1000):
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
    init_data_url = './data/init/'
    # test for dice rolls(single)
    test = [0, 0, 0, 0, 0, 0]
    for i in range(10000):
        test[roll_dice() - 1] += 1
    print(f'the distribution of dice rolls: {test}')

    # test for initiate map
    ph, pp, tp = initiate_map(init_data_url)
    harbor_point_list = list(set([sub_li[0] for sub_li in ph]))
    terrain_type_list = get_terrain_resource()
    terrain_number_list = get_roll_num_list(terrain_type_list)
    idx_terrain_dict, terrain_dict = generate_terrain_dict(terrain_type_list, terrain_number_list, tp)
    point_terrain_dict, point_probability, point_probability_sort_list = point_terrain_creator(tp, idx_terrain_dict)

    simulation_times = 1000
    val1 = []
    val2 = []

    for i in range(simulation_times):
        player1 = player_generater(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                   point_probability)
        player2 = player_generater(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                   point_probability)

        times1, game_pass, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = settlement_simulation(
            player1, terrain_dict, point_probability, pp, harbor_point_list, max_round=200, vp=10, epoch=50)
        times2, game_pass, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec \
            = city_simulation(player2, terrain_dict, point_probability, pp, harbor_point_list, max_round=200, vp=10,
                              epoch=50)

        val1.append(times1)
        val2.append(times2)

    vis_two_round(val1, val2, "settlement prefer", "city prefer", 1, simulation_times=simulation_times)

    # hypothesis 2 simulation:
    simulation_times = 1000
    val1 = []
    val2 = []

    for i in range(simulation_times):
        player1 = player_generater(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                   point_probability)
        player2 = player_generater(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                   point_probability)

        times1, game_pass, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec = harbor_simulation(
            player1, terrain_dict, point_probability, pp, harbor_point_list, max_round=200, vp=10, epoch=50)
        times2, game_pass, vp_rec, set_rec, city_rec, road_rec, brick_rec, lum_rec, ore_rec, grain_rec, wool_rec \
            = city_simulation(player2, terrain_dict, point_probability, pp, harbor_point_list, max_round=200, vp=10,
                              epoch=50)

        val1.append(times1)
        val2.append(times2)

    vis_two_round(val1, val2, "harbor prefer", "city prefer", 2, simulation_times=simulation_times)