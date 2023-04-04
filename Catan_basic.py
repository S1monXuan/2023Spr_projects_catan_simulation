import random

import Elements


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


if __name__ == '__main__':
    test = [0, 0, 0, 0, 0, 0]
    for i in range(10000):
        test[roll_dice() - 1] += 1
    print(test)
