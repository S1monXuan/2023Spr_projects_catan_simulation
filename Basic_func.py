from Universal_func import *


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
    Idea from:
        Wikipedia contributors. “Breadth-first Search.” Wikipedia, 27 Feb. 2023, en.wikipedia.org/wiki/Breadth-first_search.

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
    if (time + 1) % epoch == 0:
        print("==============================")
        print(f"player status after round {time + 1}")
        print("Player status display:")
        player.print_player()

    if time == max_round - 1:
        print("==============================")
        print("game over, player failed to reach victory point")

    return False


def simulation_process(player, terrain_dict, point_probability, pp, harbor_point_list, strategy, max_round=200, vp=10,
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
    if strategy == 3:
        dest_harbor_point, dest_path = shortest_harbor_path(player.settlements, player.reachable_points, pp,
                                                            harbor_point_list)
    ## for settlement prefer strategy
    max_round, vp, gamePass = max_round, vp, False
    reclist = get_rec_list(player)
    used_round = max_round
    for time in range(max_round):
        # step 1: get resource
        get_resource(player, terrain_dict)
        # step 2: check for any possible build process
        if strategy == 1:
            settlement_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
        elif strategy == 2:
            city_upgrade_prefer(player, terrain_dict, point_probability, pp, harbor_point_list)
        elif strategy == 3:
            harbor_build_prefer(player, terrain_dict, point_probability, pp, harbor_point_list, dest_path,
                                dest_harbor_point)
        # step 3: store current status into resource recorder for later display
        reclist = get_rec_list(player)
        # step 4: check if player wins, if so, display and return all results
        gamePass = check_game_pass(player, time, vp, epoch, max_round)
        if gamePass:
            used_round = time
            break
    resRecoder = ResRecoder(used_round, gamePass)
    return resRecoder, reclist


def vis_two_round(round_rec1: list, round_rec2: list, round1_type: str, round2_type: str, hypo: int, max_round,
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
    plt.savefig(output_name)
    plt.close()

    bar_vis(round_rec1, round_rec2, round1_type, round2_type)


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
    print(header)
    for resource in resource_list:
        print(resource)

    # stroe situation into a csvfile
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=',')
        writer.writerows(header)


def dice_visualization(num_list):
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
    plt.savefig(output_name)
    plt.close()


def bar_vis(val1: list, val2: list, name1, name2):
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
    plt.legend([name1, name2, "draw"])
    plt.savefig(output_name)
    plt.close()