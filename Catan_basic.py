import random

import pandas as pd

from Elements import Player, Block


def roll_dice() -> int:
    """
    Rolling a dice, would return random number between 1 - 6
    :return: Integer between 1 - 6
    """
    return random.randint(1, 6)


def initiate_map(default_setting_url, maps):
    # """
    # Would initiate a map in this simulation
    # :return:list with all terrains with their unique resource and number
    # """
    # step 1 read point_harbor data
    # link point_harbor using list(harbor)[list(point)]
    p_h_file = default_setting_url + 'point_harbor.csv'
    p_h_data = pd.read_csv(p_h_file).to_numpy()

    # step 2 read point_point data
    # link point_point using list(point1)[list(point2)]
    p_p_file = default_setting_url + 'point_point.csv'
    p_p_data = pd.read_csv(p_p_file).to_numpy()

    # step 3 read terrain_point data
    # link terrain_point using list(terrain)[list(point)]
    t_p_file = default_setting_url + 'terrain_point.csv'
    t_p_data = pd.read_csv(t_p_file).to_numpy()
    a = 0


def simulation(player: Player, target_point=10):
    # simulate a round process
    if player.vp == target_point:
        # if it reaches vp point, just return the point and return
        raise NotImplemented
    else:
        num = roll_dice() + roll_dice()


if __name__ == '__main__':
    test = [0, 0, 0, 0, 0, 0]
    for i in range(10000):
        test[roll_dice() - 1] += 1
    print(test)
