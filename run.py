import base3 as base
from rocketship import RocketShip

#mod, results = base.run('test', 'datasets/long_deltav.csv')
opts = {'MIPGap': 0.50, 'MIPFocus': 3, 'TimeLimit': 600, 'BranchDir': 1}

ship = RocketShip(90000, 20000000, thrust_scale=1.5)

for gamma in [3000]:
    base.run('alt' + str(gamma), 'datasets/revamp_deltav.csv', gurobi_opts=opts, gamma=gamma, ship=ship)


#[0, 1000, 2000, 2500, 3000, 3250, 3500, 3750, 4000, 4250, 4500]
