# -*- coding: utf-8 -*-
"""
Transportation of Fuel Payloads in Space

Contributors:
  Duncan Anderson
  Adam Kehoe
  Brent Austgen
"""

from pyomo.environ import *
from pyomo.opt import *
import pandas as pd
import sys
import math as m

fuelcost_df = pd.read_csv(r'C:\Users\DAnderson\Documents\Grad School\asteroid\output.csv')


mod = ConcreteModel()

# sets

def rangeinit(model):
    return (i for i in range(120,330,30))
mod.routes = Set(initialize=rangeinit)

mod.time = Set(initialize=range(0, 500), ordered=True)
#mod.routes = Set(initialize=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
mod.nodes = Set(initialize=['Earth', 'Ceres','Mars'])
mod.edges = Set(within=mod.nodes*mod.nodes, initialize=[
    ('Earth', 'Ceres'),
    ('Ceres', 'Earth'),
    ('Mars', 'Ceres' ),
    ('Ceres', 'Mars' ) 
])

def get_fuel_cost(mod, t, i, j, r):
    global fuelcost_df
    #return float(fuelcost_df[fuelcost_df.t == t][i[0]+j[0]+'f' + str(r)])# + '0'])
    return float(fuelcost_df[fuelcost_df.t == t][i[0]+j[0]+'f' + str(r)])# + '0'])


def get_fuel_prod(mod, t, i):
    # can be changed to import when we have real data
    return float(5000 if i == 'Ceres' else 0)

# parameters
mod.ship_fuel_cap = 800000
mod.num_ships = 1
#Non model parameters for calculating fuel costs
ship_mass = 120000
thrustcount = 15
Impulse = 482
g = .00981
print('modifying delta-v inputs into fuel costs')
for col in fuelcost_df[:]:
    if col != 't' and col != 'Calendar Date':
        if col[:1] == 'C':
            fuelcost_df[col] = fuelcost_df[col].apply(lambda x: (ship_mass+mod.ship_fuel_cap)*(1-1/m.exp(x/(g*Impulse*thrustcount))))
        else:
            fuelcost_df[col] = fuelcost_df[col].apply(lambda x: (ship_mass)*(m.exp(x/(g*Impulse*thrustcount))-1))
print('exporting fuel cost matrix')
fuelcost_df.to_csv(r'c:\users\DAnderson\Documents\Grad School\asteroid\realfuelcost'+runid+'.csv',',')
print('fuel cost matrix exported')
mod.fuel_cost = Param(mod.time, mod.edges, mod.routes,
                      initialize=get_fuel_cost)
mod.fuel_prod = Param(mod.time, mod.nodes,
                      initialize=get_fuel_prod)



#m0*(1-1/exp(x/tig)) = m0-mf

# variables
mod.launch = Var(mod.time, mod.edges, mod.routes,
                 domain=NonNegativeIntegers)
mod.ship_storage = Var(mod.time, mod.nodes, domain=NonNegativeIntegers)
mod.fuel_storage = Var(mod.time, mod.nodes, domain=NonNegativeReals,
                       initialize=0)
mod.fuel_spill = Var(mod.time, mod.nodes, domain=NonNegativeReals,
                     initialize=0)

# objective
def objective(mod):
    return mod.fuel_storage[mod.time[-1], 'Earth'] + mod.fuel_storage[mod.time[-1], 'Mars']
mod.objective = Objective(rule=objective, sense=maximize)

# helper functions
def edges_leave(mod, i):
    return [edge for edge in mod.edges if edge[0] == i]

def edges_enter(mod, i):
    return [edge for edge in mod.edges if edge[1] == i]

# constraints
def con_ship_flow_balance(mod, t, i):
    if t > 0:
        return mod.ship_storage[t, i] == mod.ship_storage[t-1, i] - \
            sum(mod.launch[t-1, e, r]
                for e in edges_leave(mod, i) for r in mod.routes) + \
            sum(mod.launch[t-r-1, e, r]
                for e in edges_enter(mod, i) for r in mod.routes if t-r-1 >= 0)
    else:
        return mod.ship_storage[t, i] == (mod.num_ships if i == 'Ceres' else 0)
mod.con_ship_flow_balance = Constraint(mod.time, mod.nodes,
                                       rule=con_ship_flow_balance)

def con_fuel_flow_balance(mod, t, i):
    if t > 0:
        return mod.fuel_storage[t, i] == mod.fuel_storage[t-1, i] - \
            sum(mod.launch[t-1, e, r] * \
                (mod.ship_fuel_cap if i == 'Ceres' else mod.fuel_cost[t-1, e, r])
                for e in edges_leave(mod, i) for r in mod.routes) + \
            sum(mod.launch[t-r-1, e, r] * \
                ((mod.ship_fuel_cap - mod.fuel_cost[t-r-1, e, r])
                if e[0] == 'Ceres' else 0) for e in edges_enter(mod, i)
                for r in mod.routes if t-r-1 >= 0) + \
            mod.fuel_prod[t-1, i] - \
            mod.fuel_spill[t, i]
    else:
        return mod.fuel_storage[t, i] == 0
mod.con_fuel_flow_balance = Constraint(mod.time, mod.nodes, rule=con_fuel_flow_balance)

def con_ceres_fuel_cap(mod, t):
    # note: if bound is infinity, there is no spill
    return mod.fuel_storage[t, 'Ceres'] <= float('inf')
mod.con_ceres_fuel_cap = Constraint(mod.time, rule=con_ceres_fuel_cap)

solver = pyomo.opt.SolverFactory('gurobi')
results = solver.solve(mod, tee=True, keepfiles=True)
results.write()


e_cap = []
c_cap = []
m_cap = []
l_CE = []
l_EC = []
l_CM = []
l_MC = []
f_use = []
runid = '500_outputtest'

launch_dat = [[],[],[],[],[],[]]
for t in mod.time:
    f_use.append(0)
    for (i,j) in mod.edges:
        for r in mod.routes:
            if mod.launch[t,(i,j),r].value != None:     
                x = mod.launch[t,(i,j),r].value
            rstr = i[0] + j[0] + 'f' + str(r)
            f_use[t] += x * fuelcost_df[rstr][t]
            #print(t, f_use[t])
            if x != 0 and x is not None:
                print(t,(i,j),r,x)
                launch_dat[0].append(t)
                launch_dat[1].append(i)
                launch_dat[2].append(j)
                launch_dat[3].append(r)
                launch_dat[4].append(t+r)
                launch_dat[5].append(x)
for t in mod.time:
    e_cap.append(mod.fuel_storage[t,'Earth'].value)
    c_cap.append(mod.fuel_storage[t,'Ceres'].value)
    m_cap.append(mod.fuel_storage[t,'Mars'].value)
   
   
#output_df = pandas.DataFrame(np.column_stack([mod.time
#                             ,mod.fuel_storage[t, 'Earth'].value
#                             ,mod.fuel_storage[t, 'Ceres'].value
#                             ,mod.fuel_storage[t, 'Mars'].value]),
#                             columns = ('t','e','c','m'), index = t)
        
output_df = pd.DataFrame(
        {'t': mod.time,
         'e_cap': e_cap,
         'c_cap': c_cap,
         'm_cap': m_cap,
         'f_use': f_use} )  
output_df.to_csv(r'c:\users\DAnderson\Documents\Grad School\asteroid\capacityresults'+runid+'.csv',',')
output_df2 = pd.DataFrame(
        {'launch_time': launch_dat[0],
         'origin': launch_dat[1],
         'destination': launch_dat[2],
         'travel_time': launch_dat[3],
         'arrival_time': launch_dat[4],
         'shipcount': launch_dat[5]} )  
output_df.to_csv(r'c:\users\DAnderson\Documents\Grad School\asteroid\launchresults'+runid+'.csv',',')
