from Compete_func import *

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

    strategy_list = ["settlement_prefer", "city_prefer"]
    model_hypothesis(strategy_list, simulation_times, max_round, vp, epoch, 1, pp, tp, ph)

    strategy_list = ["harbor_prefer", "city_prefer"]
    model_hypothesis(strategy_list, simulation_times, max_round, vp, epoch, 2, pp, tp, ph)
