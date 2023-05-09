from Basic_func import *

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
    dice_visualization(test)

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
    simulation_times, max_round, vp, epoch = 1000, 300, 8, 50
    val1 = []
    val2 = []
    val3 = []

    for i in range(simulation_times):
        # cereate a new board and save
        harbor_point_list = list(set([sub_li[0] for sub_li in ph]))
        terrain_type_list = get_terrain_resource()
        terrain_number_list = get_roll_num_list(terrain_type_list)
        idx_terrain_dict, terrain_dict = generate_terrain_dict(terrain_type_list, terrain_number_list, tp)
        point_terrain_dict, point_probability, point_probability_sort_list = point_terrain_creator(tp, idx_terrain_dict)
        filename = 'data/border/border' + str(i) + '.csv'
        board_save(point_terrain_dict, idx_terrain_dict, filename)

        # GeneratePlayer


        player1 = player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                   point_probability, "settlement_prefer", harbor_point_list)
        player2 = player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                   point_probability, "city_prefer", harbor_point_list)
        player3 = player_generator(point_probability_sort_list, pp, point_terrain_dict, idx_terrain_dict,
                                   point_probability, "harbor_prefer", harbor_point_list)

        recoder1, rec1 = simulation_process(
            player1, terrain_dict, point_probability, pp, harbor_point_list, 1, max_round=max_round, vp=vp, epoch=epoch)
        recoder2, rec2 = simulation_process(
            player2, terrain_dict, point_probability, pp, harbor_point_list, 2, max_round=max_round, vp=vp, epoch=epoch)
        recoder3, rec3 = simulation_process(
            player3, terrain_dict, point_probability, pp, harbor_point_list, 3, max_round=max_round, vp=vp, epoch=epoch)

        val1.append(recoder1.used_round)
        val2.append(recoder2.used_round)
        val3.append(recoder3.used_round)

    print(f"Avg for val1: {sum(val1) / len(val1)}, val2: {sum(val2) / len(val2)}, val3: {sum(val3) / len(val3)}")

    vis_two_round(val1, val2, "settlement prefer", "city prefer", 1, max_round, simulation_times=simulation_times)
    vis_two_round(val3, val2, "harbor prefer", "city prefer", 2, max_round, simulation_times=simulation_times)