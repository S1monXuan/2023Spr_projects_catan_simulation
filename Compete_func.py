from matplotlib.ticker import PercentFormatter

from Universal_func import *


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
    if own_harbor(player, harbor_point_list) or (len(harbor_path) < (15 - player.road_num)):
        # step 2: if already have a harbor, do as settlement first
        settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
    else:
        # build road to the nearest harbor until it build a settlement in harbor
        trade_supporter(player, get_trade_rate(player, harbor_point_list), ResourceDict("road"))
        while road_possible(player, harbor_point_list):
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
    player.reachable_points = list(set(player.reachable_points))


def shortest_harbor_path(player: Player, pp, harbor_point_list: list,
                         player_list: list) -> [int, list]:
    """
    get the nearest point(harbor) to the point and the shortest path to the point
    :param player:
    :param pp:
    :param harbor_point_list:
    :return: int represent the point contians the harbor, list contians the road to build the path
    """
    cur_settlements = player.settlements.copy()
    cur_settlements.extend(player.cities)

    reachable_list = player.reachable_points.copy()

    harbor_point = 0
    res_list = [*range(0, 54, 1)] # output, default len 54

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
                # remove the point if its a harbor point and its neighbor already have a building

    for start_point in reachable_list:
        cur_path = find_shortest_path(start_point, pp, cur_harbor_point_list, building_points, player_list)

        if (len(cur_path) < len(res_list)) and (len(cur_path) > 0):
            res_list = cur_path
            harbor_point = res_list[len(res_list) - 1]

    return harbor_point, res_list


def find_shortest_path(start_point: int, pp: list, harbor_point_list: list, cur_settlements: list, player_list: list) -> list:
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
                if (neighbor not in cur_route) and (neighbor not in cur_settlements): # check if the neighbor not in current player route, already build a buildinging

                    # check whether there already exists a road between neighbor point and the current point by all players
                    road_already = False
                    for p in player_list:
                        if (neighbor in p.reachable_points) and (cur_point in p.reachable_points):
                            road_already = True

                    if not road_already:
                        # no road exists between two point
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
        player.print_player()

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

        dest_harbor_point, dest_path = shortest_harbor_path(player, pp,
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


def vis_two_round(win_count: dict, res_point_dict: dict, hypo: int, compete: False,
                  vp = 10):
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
    y_recs = []
    y_types = []
    for type, point in res_point_dict.items():
        y_recs.append(point)
        y_types.append(type)
        print(point)

    print(y_recs)
    print(y_types)
    print(len(y_recs), len(y_types))

    # visualization
    x_val = [*range(1, vp + 1, 1)]

    title = f"Vis_for_Hypothesis_{hypo}"

    plt.title(title)
    plt.xlabel("victory points")
    plt.ylabel("VP Percentage")
    plt.hist(y_recs[0], bins=11, weights=np.ones(len(y_recs[0])) / len(y_recs[0]), alpha = 0.5)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

    plt.hist(y_recs[1], bins=11, weights=np.ones(len(y_recs[0])) / len(y_recs[0]), alpha = 0.5)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.legend(y_types)
    output_name = './data/output/' + title
    if compete:
        output_name += '_Compete'
    plt.savefig(output_name)
    plt.close()

    bar_vis(win_count, compete)


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

    # store situation into a csvfile
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


def bar_vis(win_count: dict, compete=False):
    names = []
    count = []
    for idx, val in win_count.items():
        names.append(idx)
        count.append(val)

    title = "pie_" + names[0] + "_" + names[1]
    plt.pie(count, labels=names)
    output_name = './data/output/' + title
    if compete:
        output_name += '_Compete'
    plt.legend(names)
    plt.savefig(output_name)
    plt.close()


def compete_player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict, point_probability,
                             strategy_list, harbor_point_list) -> list:
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


def model_hypothesis(strategy_list, simulation_times, max_round, vp, epoch, hypothesis_idx, pp, tp, ph):
    res_point_dict = {}
    win_count = {}
    res_dict = {}
    for strategy in strategy_list:
        res_point_dict[strategy] = []
        win_count[strategy] = 0
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
                                             point_probability, strategy_list, harbor_point_list)

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
                    # print(curli)
                    curli.append(times + 1)
                    res_dict[player.strategy] = curli
                    print(f"{player.strategy}: {times + 1}")
                    finishcnt += 1
                    break
            # Each player start their turn

        # get min player
        max_vp = 0
        player_strategy = ''
        for player in player_li:
            if max_vp < player.vp:
                max_vp = player.vp
                player_strategy = player.strategy
            res_point_dict[player.strategy].append(player.vp)

        win_count[player_strategy] += 1

    print(win_count)
    print(res_point_dict)

    # print(res_dict)
    val1 = []
    val2 = []
    for idx, lis in res_point_dict.items():
        if idx == "city_prefer":
            val2 = lis
        else:
            val1 = lis

    vis_two_round(win_count, res_point_dict, hypothesis_idx, vp=vp, compete=True)
