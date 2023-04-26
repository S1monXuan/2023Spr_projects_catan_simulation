import random
import pandas as pd
from Elements import Player, Terrain, Point


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
    print("resources")
    for terrain_idx in terrain_list:
        cur_terrain_res = idx_terrain_dict[terrain_idx].resource
        print(cur_terrain_res)
        player.resources_list[cur_terrain_res] += 1

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
    resource_turn = 0

    for idx in range(5):
        # check if the needed resource is redundant
        if idx in target_list:
            resource_lack += max(needed_dict[idx] - player.resources_list[idx], 0)
            resource_turn += int(max(player.resources_list[idx] - needed_dict[idx], 0) / trade_rate)
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
    building_neighbor = list(set(building_neighbor)) # remove all redundant point

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
                    cur_res = int(player.resources_list[idx] - needed_dict[idx] / trade_rate)
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
                    cur_res = int(player.resources_list[idx] - needed_dict[idx] / trade_rate)
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
    print(f"Cuurent possible point list: {possible_point}, len: {len(possible_point)}")
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
                        cur_res = int(player.resources_list[idx] - needed_dict[idx] / trade_rate)
                        trans_res = min(cur_res, need_res)
                        player.resources_list[idx] -= trans_res * trade_rate
                        player.resources_list[need_id] += trans_res
                        need_res -= trans_res

        # find all possible point for road building
        building_point = []

        # add all possible neighbors for player_reachable_points
        for reach_point in player.reachable_points:
            for nei_point in pp[reach_point]:
                if nei_point not in player.settlements and nei_point not in player.cities and nei_point not in player.reachable_points:
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
    if len(player.settlements) == 0:
        while settlement_possible(player, harbor_point_list, pp):
            print("settlement_build_prefer() pass")
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
    if len(player.settlements) == 5:
        while city_possible(player, harbor_point_list):
            build_a_city(player, point_probability, harbor_point_list)
            # check if resource available for building a settlement: while loop
    # building a settlement can only be considered if there does not have any settlement waiting for upgrading
    while road_possible(player, harbor_point_list):
        while settlement_possible(player, harbor_point_list, pp):
            build_a_settlement(player, point_probability, pp, harbor_point_list)
            # check if resource available for building a road + settlement: for loop * 2
        for _ in range(2):
            if road_possible(player, harbor_point_list):
                build_a_road(player, point_probability, pp, harbor_point_list)
            if settlement_possible(player, harbor_point_list, pp):
                build_a_settlement(player, point_probability, pp, harbor_point_list)


def harbor_build_prefer(player: Player, terrain_dict, point_probability, pp, harbor_point_list) -> None:
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

    # check wether player owns a harbor
    if own_harbor(player, harbor_point_list):
        # step 2: if already have a harbor, do as settlement first
        settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    else:
        # build road to the nearest harbor until it build a settlement in harbor
        neareast_point, path = get_harbor_path(player.reachable_points, pp, harbor_point_list)


def get_harbor_path(reachable_list: list, pp: list, harbor_point_list: list):
    shortest_step = 100
    raise NotImplementedError


def shortest_harbor_path(reachable_list: list, pp, harbor_point_list: list) -> [int, list]:
    """
    get the nearest point(harbor) to the point and the shortest path to the point
    :param player:
    :param pp:
    :param harbor_point_list:
    :return: int represent the point contians the harbor, list contians the road to build the path
    """
    harbor_point = 0
    res_list = []
    for start_point in reachable_list:
        cur_res_list = []
        cur_path = [start_point]
        find_shortest_path(start_point, pp, harbor_point_list, cur_path, cur_res_list)

        print(cur_res_list)

        if len(cur_res_list) < len(res_list):
            res_list = cur_res_list.copy()
            harbor_point = res_list[len(res_list) - 1]

    return harbor_point, res_list


def find_shortest_path(start_point: int, pp: list, harbor_point_list: list, cur_path: list, cur_res_list: list):
    """
    Support function to find the shortest path start from start_point, Using BFS
    :param start_point: the start point for the path, default will not be the harbor_point_list
    :param pp: point-point list
    :param harbor_point_list: list contains all possible result
    :param cur_path: list for all current visited path
    :param res_list: return current best route
    :return: int represent the point contains the harbor, list contains the road to build the path
    """
    if start_point in harbor_point_list:
        # if len(cur_path) <= len(cur_res_list):
        cur_res_list.append(cur_path.copy())
        tmp = 1
        return
    else:
        for neighbor in pp[start_point]:
            if neighbor not in cur_path:
                # not visited yet
                cur_path.append(neighbor)
                find_shortest_path(neighbor, pp, harbor_point_list, cur_path, cur_res_list)
                cur_path.pop()
        cur_path.pop()


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
    print(harbor_point_list)
    # print(len(ph), len(pp), len(tp))
    # print("ph, pp, tp")
    # print(ph)
    # print(pp)
    # print(tp)
    # print("===============================")

    # create a terrain list using p_p, p_h, t_p
    terrain_type_list = get_terrain_resource()
    terrain_number_list = get_roll_num_list(terrain_type_list)
    idx_terrain_dict, terrain_dict = generate_terrain_dict(terrain_type_list, terrain_number_list, tp)
    # print("terrain_type_list, terrain_number_list, idx_terrain_dict, terrain_dict")
    # print(terrain_type_list)
    # print(terrain_number_list)
    # print(idx_terrain_dict)
    # print(terrain_dict)
    # print("===============================")

    point_terrain_dict, point_probability, point_probability_sort_list = point_terrain_creator(tp, idx_terrain_dict)
    # print("point_terrain_dict, point_probability, point_probability_sort_list")
    # print(point_terrain_dict)
    # print(point_probability)
    # print(point_probability_sort_list)
    # print("===============================")

    # for simulation
    # before starting simulation loop, create a player
    player = player_generater(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict, point_probability)

    # Hypothesis 1
    #     Upgrading a city is a better choice than building a new settlement
    # Hypothesis 2
    #     Get a harbor at first is better than obtain a new source

    ## step 1: get the roll number
    dice_num = roll_dice() + roll_dice()
    # judge whether the player get resource using terrain_dict
    # terrain_resource = terrain_dict[dice_num]
    terrain_resources = [[t.point, t.resource] for t in terrain_dict[dice_num]]
    # print(terrain_resources)

    ## step 2: find all player owned place, add resource
    # add 1 resouce to all settlments
    player_buildings = player.settlements
    if dice_num != 7:  # if the number is 7, do not have any resource, jump out for further report
        for building_point in player_buildings:
            for [des_point_list, point_resource] in terrain_resources:
                player.resources_list[point_resource] += 1 if building_point in des_point_list else 0

        # print("Check player after add resource for settlement")
        # player.print_player()

        # print(f"create city in point {terrain_resources[0][0][0]} for test")
        # player.cities.append(terrain_resources[0][0][0])
        # add 2 resources to all settlements
        player_buildings = player.cities
        for building_point in player_buildings:
            for [des_point_list, point_resource] in terrain_resources:
                player.resources_list[point_resource] += 2 if building_point in des_point_list else 0
        # print("Check player after add resource for city")
        # player.print_player()

    # test for each round
    ## Case 1, h1: situation 1: if there has a settlment, then upgrade the city
    # prerequest1: player would upgrade the city with highest probability

    # city_upgrade_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)

    ## Case 2, h1: suituatnio 2: if build a settlement possible,build a settlement first

    ### check for case 1 and case 2 for hypothesis 1
    # print("==============================")
    # print("settlement_build_test")
    # player.set_resource_list([100, 100, 100, 100, 100])
    # print("do city upgrade prefer:")
    # city_upgrade_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    #
    # print("current status")
    # player.print_player()
    # settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    # print("after settlement_build")
    # player.print_player()
    # player.set_resource_list([10, 20, 2, 3, 3])
    # print("current status")
    # player.print_player()
    # settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    # print("after settlement_build")
    # player.print_player()

    # print("Current player status")
    # player.print_player()
    # print("=========================")
    #
    # print("test road build, add 1 brick, 1 lumber ")
    # player.resources_list[0] += 1
    # player.resources_list[1] += 1
    # # test road build:
    # build_a_road(player, point_probability, pp, harbor_point_list)
    # player.print_player()
    # print("=========================")
    #
    # print("test settlement build, add 1 brick, lumber, wool, grain")
    # player.resources_list[0] += 1
    # player.resources_list[1] += 1
    # player.resources_list[3] += 1
    # player.resources_list[4] += 1
    # # test settlement build:
    # build_a_settlement(player, point_probability, pp, harbor_point_list)
    # player.print_player()
    # print("=========================")
    # print("test settlement city, add 2 grain, 3 ore")
    # player.resources_list[2] += 3
    # player.resources_list[3] += 2
    # # test city build
    # build_a_city(player, point_probability, harbor_point_list)
    # player.print_player()
    # print("=========================")

    # test for add resource
    # player.set_resource_list([0,0,0,0,0])
    # player.print_player()
    #
    # # check trade resource
    # print("==========res: [5, 0, 0, 1,1]========")
    # player.set_resource_list([5,0,0,1,1])
    # player.print_player()
    # print(road_possible(player, harbor_point_list), settlement_possible(player, harbor_point_list, pp), city_possible(player, harbor_point_list))
    #
    # print("==========res: [5, 0, 0, 0,0]========")
    # player.set_resource_list([0,4,2,2,0])
    # player.print_player()
    # print(road_possible(player, harbor_point_list), settlement_possible(player, harbor_point_list, pp), city_possible(player, harbor_point_list))

    ## h1, situation 2, first check whether upgrading a settlement is possible
    # check if resource available for building a settlement: while loop

    # check if resource available for building a road + settlement: for loop * 2

    # check if resource available for upgrading a city: while loop

## h2, situation 1, first check whether upgrading a settlement is possible same as settlement upgrading

## h2, situation 2, check whether the player obtains a harbor, if so, same strategy as 1, else build road until reach harbor

# try shortest path find
    point, path = shortest_harbor_path(player.reachable_points, pp, harbor_point_list)
    print(point)
    print(path)

    ## step4: end this round do nothing

    # if player.resources_list[2] >= 3 and player.resources_list[3] >= 2 and len(player.settlements) > 0:
    #     upgrade_city(player, )
    # else

    # generate simulation steps
    # for ite in range(1000):
    #     # jump out when run 100 times or reach vp point requirement
    #     if player.vp == 10: break
    #     # print results every 50 rolls
    #     if ite % 50 == 0:
    #         # show the result of current player situation for every 50 rounds
    #         # display current situation
    #         player.print_player()
    #
    #     # roll a dice and get the point
    #     dice_num = roll_dice()
    #     # check whether the player would gain resource
    #     gain_resource(player, dice_num, );

    # check whether the player could build a road and decide the next road point

    # check whether the player could build a settlement or upgrade to a city

    # check whether the player could build
