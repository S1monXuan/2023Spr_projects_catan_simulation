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
    p_h_data = list(pd.read_csv(p_h_file).to_numpy() - 1)
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
        t_p[idx - 1].append(point)
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
    terrain_resource_list = [1, 3, 4, 3, 4, 4]
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
        if terrain_resource_list[idx] == 0:
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
    num_pro_list = [0,0,1,2,3,4,5,0,5,4,3,2,1]
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
    buildable_list = []
    for point in reachable_list:
        buildable_list.extend(pp[point])
    # remove all unreachable points
    for point in point_list:
        # if point in un_buildable_list:
        #     un_buildable_list.remove(point)
        unreachable_points = pp[point]
        for near_point in unreachable_points:
            if near_point in buildable_list:
                buildable_list.remove(near_point)
    return point2 in buildable_list


if __name__ == '__main__':
    init_data_url = './data/init/'
    # test for dice rolls(single)
    test = [0, 0, 0, 0, 0, 0]
    for i in range(10000):
        test[roll_dice() - 1] += 1
    print(f'the distribution of dice rolls: {test}')

    # test for initiate map
    ph, pp, tp = initiate_map(init_data_url)
    # print(len(ph), len(pp), len(tp))
    # print(ph)
    # print(pp)
    # print(tp)

    # create a terrain list using p_p, p_h, t_p
    terrain_type_list = get_terrain_resource()
    terrain_number_list = get_roll_num_list(terrain_type_list)
    idx_terrain_dict, terrain_dict = generate_terrain_dict(terrain_type_list, terrain_number_list, tp)
    # print(terrain_type_list)
    # print(terrain_number_list)
    # print(terrain_dict)

    point_terrain_dict, point_probability, point_probability_sort_list = point_terrain_creator(tp, idx_terrain_dict)
    # print(point_terrain_dict)
    # print(point_probability)
    # print(point_probability_sort_list)


    # for simulation
    # before starting simulation loop, create a player
    player = Player()
    # create default settlements
    # if the first two points are buildable, choose the first 2. Else choose the first and the most suitable that could be built
    point2 = 1
    def_point_list = [*range(0, 54, 1)]
    while not point_buildable([point_probability_sort_list[0]], point_probability_sort_list[point2], pp, def_point_list):
        point2 += 1
    player.settlements.append(point_probability_sort_list[point2])
    player.settlements.append(point_probability_sort_list[0])

    # get reachable points for default points

    # get initial resource for the point1

    print(point2)




