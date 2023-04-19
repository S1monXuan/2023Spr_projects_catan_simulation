# 2023Spr_projects
It is the final project for UIUC IS 597 pr. Created by Xinmai Xuan (xinmaix2).
It is an ongoing project and might be finished in following 2-3 weeks.

# Phrase 1:

## Elements of Catan

### terrain
The game board is consisted by 19 different terrains. Each terrain owns a specific number and a generated resource. Player would get the resource the time they build a settlement or a cicy besides the terrain which owns the same number as the results of  dice rolls.
- resource type
There are six different resources:
  - Hills: Resources number 1, Produce Brick, 3 in total
  - Forest: Resources number 2, Produce Lumber, 4 in total
  - Mountains: Resources number 3, Produce Ore, 3 in total
  - Fields: Resources number 4, Produce Grain, 4 in total
  - Pasture: Resources number 5, Produce Wool, 4 in total
  - Desert: Resources number 0 Produce Nothing, 1 in total 
- Number
Each terrain, except Desert, has a special points between 2 to 14, except 7.
- Harbor
Some terrains located on the edge of the board may have harbors. There are 2 main types of harbors: Generic Harbor and Special Harbor.
Player could exchange 3 identical resources for any 1 other resource during trade phase if owns a generic Harbor.
Player could exchange 2 designated resources for any 1 other resource during trade phase if owns a special Harbor, based on they type of special harbor.
  - There are 4 generic harbors and 5 special harbors.  
    - generic harbor: Harbor number 6
    - special hill: number 1
    - special forest: number 2
    - special mountains: number 3
    - special fields: number 4
    - special pasture: number 5
- Point
The point of the corner of each terrain. Each terrain has 6 points. Player could build settlement or upgrade a settlement on some point they could use.

### Building Types
There are 4 building options in Catan, however, we only use 3 types in this model
- Road
Cost: 1 lumber and 1 brick
Road connects two points. Settlement can only be build on points that connected by roads.
- Settlement
Cost: 1 brick, 1 lumber, 1 grain, 1 wool
Each settlement could gain 1 resource if possible. Settlement can not build on 2 neighbor points.
- City
Cost: 2 grain, 3 ore
City can only be upgraded from settlement. Each city could gain 2 resource if possible.

## Phrase of Catan


## 1 Design
- Random Variables:
Due to the real game rules and workload consideration, I listed all possible random variables that might be used in this final project. The Random variables 1 and 2 will definitely appear as random variables. Random 3 and 4, indtead, might be set as constant variables based on the workload and complexity of other projects. 	
Random Variables 1: The number of points obtained by rolling two dice. It should be simulated as triangular.
Random Variables 2: The resource distribution of each resource’s bricks.
Random Variables 3: The chance of earning resource of each resource’s bricks. 
Random Variables 4: The distributions of harbors.

- Pre-request for this Monte Carlo Simulation:
Each simulation describes the whole game process. Starting from default resources, two dice are rolled repeatedly to represent each turn. During each turn, the user could make actions such as trade with bank, trade with port, and building instructions including road, settlement, and city.  
We do not account for robber, player of development card, largest army, longest road, and any trade with other players. 
Simulation would stop when the player collect 10 points using settlements and cities. 
- 2 Validating

- 3 Experiment & Predictions

## Phrase 2:

## Phrase 3: 
