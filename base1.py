from model import *

### WRAPPER ### ---------------------------------------------------------------

def run(uid, deltav_csv, T=None, s=None, routes=None, demand_nodes=None,
        supply_nodes=None, num_ships=None, ship=None, eta=None, theta=None,
        gurobi_opts=None, path=None):
    print('starting run with unique id {}'.format(str(uid)))

    print('setting default parameters')
    if s is None:
        s = 5
    if routes is None:
        routes = range(200, 800, 20)
    if T is None:
        T = 14605 - max(routes)
    if demand_nodes is None:
        demand_nodes = ['Earth', 'Mars']
    if supply_nodes is None:
        supply_nodes = ['Ceres']
    if num_ships is None:
        num_ships = 1
    if ship is None:
        ship = RocketShip(mass=90000, capacity=3000000, thrust_scale=1)
    if eta is None:
        eta = 1
    if theta is None:
        theta = 0.05
    if gurobi_opts is None:
        gurobi_opts = {'Heuristics': 0.20, 'MIPGap': 0.01}
    if path is None:
        path = os.getcwd()

    nodes = demand_nodes + supply_nodes
    edges = [edge for edge in product(demand_nodes, supply_nodes)] + \
            [edge for edge in product(supply_nodes, demand_nodes)]

    print('beginning model construction')
    mod = ConcreteModel()

    print('loading DeltaV data')
    if not os.path.isfile(deltav_csv):
        print('  file {} not found, aborting'.format(deltav_csv))
    deltav_df = pd.read_csv(deltav_csv, index_col=0)

    print('initializing model parameters')
    mod.s = s
    mod.time = Set(initialize=range(0, T, s), ordered=True)
    mod.routes = Set(initialize=routes)
    mod.nodes = Set(initialize=demand_nodes + supply_nodes)
    mod.s_nodes = Set(within=mod.nodes, initialize=supply_nodes)
    mod.d_nodes = Set(within=mod.nodes, initialize=demand_nodes)
    mod.edges = Set(within=mod.nodes * mod.nodes, initialize=edges)
    mod.num_ships = num_ships
    mod.ship = ship
    mod.eta = eta
    mod.theta = theta
    mod.fuelcost_df = pd.DataFrame(index=[t for t in mod.time])
    for col in deltav_df:
        if col[0] == 'C':
            method = mod.ship.vel_to_fuel_full
        else:
            method = mod.ship.vel_to_fuel_empty
        mod.fuelcost_df[col] = deltav_df[col].apply(method)
    mod.fuel_cost = \
        Param(mod.time, mod.edges, mod.routes, initialize=get_fuel_cost)
    mod.fuel_prod = Param(mod.time, mod.s_nodes, initialize=get_fuel_prod)

    print('initializing model variables')
    mod.ship_storage = Var(mod.time, mod.nodes, domain=NonNegativeIntegers)
    mod.launch = \
        Var(mod.time, mod.edges, mod.routes, domain=NonNegativeIntegers)
    mod.fuel_storage = \
        Var(mod.time, mod.nodes, domain=NonNegativeReals, initialize=0)
    mod.fuel_spill = \
        Var(mod.time, mod.nodes, domain=NonNegativeReals, initialize=0)

    print('initializing model objective function')
    mod.objective = Objective(rule=obj_discounted_fuel, sense=maximize)

    print('initializing model constraints')
    mod.con_ship_flow_balance = \
        Constraint(mod.time, mod.nodes, rule=con_ship_flow_balance)
    mod.con_launch_init_cond = \
        Constraint(mod.edges, mod.routes, rule=con_launch_init_cond)
    mod.con_ship_init_cond = \
        Constraint(mod.nodes, rule=con_ship_init_cond)
    mod.con_fuel_flow_balance_supply = \
        Constraint(mod.time, mod.s_nodes, rule=con_fuel_flow_balance_supply)
    mod.con_fuel_flow_balance_demand = \
        Constraint(mod.time, mod.d_nodes, rule=con_fuel_flow_balance_demand)
    mod.con_fuel_init_cond = \
        Constraint(mod.nodes, rule=con_fuel_init_cond)
    mod.con_spill_init_cond = \
        Constraint(mod.nodes, rule=con_spill_init_cond)
    mod.con_fuel_cap_supply = \
        Constraint(mod.time, rule=con_fuel_cap_supply)
    mod.con_route_infeas = \
        Constraint(mod.time, mod.edges, mod.routes, rule=con_route_infeas)

    print('preparing to solve')
    solver = SolverFactory('gurobi')
    for (key, val) in gurobi_opts.items():
        solver.options[key] = val
    results = solver.solve(mod, tee=True, keepfiles=True)
    results.write()

    print('postprocessing')
    params = {
        'T': T,
        's': s,
        'theta': theta,
        'num_ships': num_ships,
        'ship_mass': ship.mass,
        'ship_capacity': ship.capacity,
        'ship_thrust_scale': ship.thrust_scale,
        's_nodes': supply_nodes,
        'd_nodes': demand_nodes,
        'routes': [r for r in routes]
    }
    filename = os.path.join(path, 'params_{}.json'.format(str(uid)))
    with open(filename, 'w') as filehandle:
        json.dump(params, filehandle)


    filename = os.path.join(path, 'fuelcost_{}.csv'.format(str(uid)))
    mod.fuelcost_df.to_csv(filename)

    t_idx = [t for t in mod.time]

    df_launch = pd.DataFrame(index=t_idx)
    for r in mod.routes:
        for (i, j) in mod.edges:
            x = pd.Series([mod.launch[t, i, j, r].value for t in mod.time],
                          index=t_idx)
            df_launch[','.join(map(str, [i, j, r]))] = x
    filename = os.path.join(path, 'launch_{}.csv'.format(str(uid)))
    df_launch.to_csv(filename)

    df_ship_storage = pd.DataFrame(index=t_idx)
    for i in mod.nodes:
        df_ship_storage[i] = \
            pd.Series([mod.ship_storage[t, i].value for t in mod.time],
                      index=t_idx)
    filename = os.path.join(path, 'ship_storage_{}.csv'.format(str(uid)))
    df_ship_storage.to_csv(filename)

    df_fuel_storage = pd.DataFrame(index=t_idx)
    for i in mod.nodes:
        df_fuel_storage[i] = \
            pd.Series([mod.fuel_storage[t, i].value for t in mod.time],
                      index=t_idx)
    filename = os.path.join(path, 'fuel_storage_{}.csv'.format(str(uid)))
    df_fuel_storage.to_csv(filename)

    df_fuel_spill = pd.DataFrame(index=t_idx)
    for i in mod.nodes:
        df_fuel_spill[i] = \
            pd.Series([mod.fuel_spill[t, i].value for t in mod.time],
                      index=t_idx)
    filename = os.path.join(path, 'fuel_spill_{}.csv'.format(str(uid)))
    df_fuel_spill.to_csv(filename)

    return mod, results
