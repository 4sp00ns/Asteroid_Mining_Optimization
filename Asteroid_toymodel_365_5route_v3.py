# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 11:25:55 2018

@author: DAnderson
"""

##ASTEROID TRAJECTORY TOY MODEL

import pyomo
import pyomo.environ as pe
import pandas
import xlwings as xw

#load the dataframe
fuelcost_df= pandas.read_csv(r'C:\Users\DAnderson\Documents\Grad School\asteroid\asteroid_toy.csv')

#create the model
model = pe.ConcreteModel()

#define the time set
model.Time = pe.Set(initialize=fuelcost_df.t, ordered=True)

#pull the fuel cost parameters from the dataframe, C for Ceres, E for Earth, 3/6/9 travel time
model.Cf3 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f30))
model.Cf6 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f60))
model.Cf9 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f90))
model.Cf12 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f120))
model.Cf15 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f150))
model.Ef3 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f30))
model.Ef6 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f60))
model.Ef9 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f90))
model.Ef12 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f120))
model.Ef15 = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].f150))
model.fuelprod = pe.Param(model.Time, initialize = lambda model,f: float(fuelcost_df[fuelcost_df.t==f].fuelprod))

#ship capacity
model.max = 400

#number of ships in the model
model.Ships = 2

#define the variables in the model
#Earth 3/6/9 launches
model.Earth3 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Earth6 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Earth9 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Earth12 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Earth15 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
#Ceres 3/6/9 launches
model.Ceres3 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Ceres6 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Ceres9 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Ceres12 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Ceres15 = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
#Ship capacity (idle) variables for Earth and Ceres
model.Earth_SCap = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
model.Ceres_SCap = pe.Var( model.Time, domain=pe.NonNegativeIntegers, initialize=0)
#Fuel quantity on Earth and Ceres (should probably rename)
model.Earth_FCap = pe.Var( model.Time, domain=pe.NonNegativeReals, initialize=0)
model.Ceres_FCap = pe.Var( model.Time, domain=pe.NonNegativeReals, initialize=0)

#Simple objective for now, maximize fuel on Earth at T=50
def obj_rule(model):
    return (
            model.Earth_FCap[1000]
            )

model.OBJ = pe.Objective(rule=obj_rule, sense = pe.maximize)

#Define the constraint sets
#Ship capacity flow balance (should rename)
model.SCap_Con = pe.ConstraintList()
#Fuel capacity flow balance (should rename)
model.FCap_Con = pe.ConstraintList()
#Initial conditions
model.Initial_Cap_Con = pe.ConstraintList()
#constraints for locking down the model when unbounded (maybe not needed any more)
model.ECheck = pe.ConstraintList()

for t in model.Time:    
    #This constraint ensures that the amount of ships in the model at any time is constant
    #Currently the flow balance constraints manage this appropriately
    #model.SCap_Con.add(
    #    model.Earth_SCap[t] + model.Ceres_SCap[t]
    #    +model.Earth3[t-3]+model.Earth3[t-2]+model.Earth3[t-1]+model.Earth3[t]
    #    +model.Earth6[t-6]+model.Earth6[t-5]+model.Earth6[t-4]+model.Earth6[t-3]+model.Earth6[t-2]+model.Earth6[t-1]+model.Earth6[t]
    #    +model.Earth9[t-9]+model.Earth9[t-8]+model.Earth9[t-7]+model.Earth9[t-6]+model.Earth9[t-5]
    #    +model.Earth9[t-4]+model.Earth9[t-3]+model.Earth9[t-2]+model.Earth9[t-1]+model.Earth9[t]
    #    +model.Ceres3[t-3]+model.Ceres3[t-2]+model.Ceres3[t-1]+model.Ceres3[t]
    #    +model.Ceres6[t-6]+model.Ceres6[t-5]+model.Ceres6[t-4]+model.Ceres6[t-3]+model.Ceres6[t-2]+model.Ceres6[t-1]+model.Ceres6[t]
    #    +model.Ceres9[t-9]+model.Ceres9[t-8]+model.Ceres9[t-7]+model.Ceres9[t-6]+model.Ceres9[t-5]
    #    +model.Ceres9[t-4]+model.Ceres9[t-3]+model.Ceres9[t-2]+model.Ceres9[t-1]+model.Ceres9[t]
    #    == model.Ships)
    
    #Couldn't find a pretty way to do this
    #The model needs to look backwards for arriving ships
    #At early t levels, attempting to look backward before t=0 crashes the model
    #so the constraints must be separately defined for these early periods.
    
    ##EARTH SHIP CAPACITY FLOW BALANCE
    if t == max(model.Time):
        model.SCap_Con.add(
            model.Earth_SCap[t-1]
            - model.Earth3[t-1] - model.Earth6[t-1] - model.Earth9[t-1] - model.Earth12[t-1] - model.Earth15[t-1]
            + model.Ceres3[t-4] + model.Ceres6[t-7] + model.Ceres9[t-10] + model.Ceres12[t-13] - model.Ceres15[t-16]
            == model.Earth_SCap[t])
    elif t > 15:
        model.SCap_Con.add(
            model.Earth_SCap[t]
            - model.Earth3[t] - model.Earth6[t] - model.Earth9[t] - model.Earth12[t] - model.Earth15[t]
            + model.Ceres3[t-3] + model.Ceres6[t-6] + model.Ceres9[t-9] + model.Ceres12[t-12] + model.Ceres15[t-15]
            == model.Earth_SCap[t+1])
    elif t > 12:
        model.SCap_Con.add(
            model.Earth_SCap[t]
            - model.Earth3[t] - model.Earth6[t] - model.Earth9[t] - model.Earth12[t] - model.Earth15[t]
            + model.Ceres3[t-3] + model.Ceres6[t-6] + model.Ceres9[t-9] + model.Ceres12[t-12]
            == model.Earth_SCap[t+1])
    elif t > 9:
        model.SCap_Con.add(
            model.Earth_SCap[t]
            - model.Earth3[t] - model.Earth6[t] - model.Earth9[t] - model.Earth12[t] - model.Earth15[t] 
            + model.Ceres3[t-3] + model.Ceres6[t-6] + model.Ceres9[t-9]
            == model.Earth_SCap[t+1])
    elif t > 6:
        model.SCap_Con.add(
            model.Earth_SCap[t]
            - model.Earth3[t] - model.Earth6[t] - model.Earth9[t] - model.Earth12[t] - model.Earth15[t] 
            + model.Ceres3[t-3] + model.Ceres6[t-6]
            == model.Earth_SCap[t+1])
    elif t > 3:
        model.SCap_Con.add(
            model.Earth_SCap[t]
            - model.Earth3[t] - model.Earth6[t] - model.Earth9[t] - model.Earth12[t] - model.Earth15[t] 
            + model.Ceres3[t-3]
            == model.Earth_SCap[t+1])
    else:
        model.SCap_Con.add(
            model.Earth_SCap[t]
            - model.Earth3[t] - model.Earth6[t] - model.Earth9[t] 
            
            == model.Earth_SCap[t+1])
    ####CERES SHIP CAPACITY FLOW BALANCE    
    if t == max(model.Time):
        model.SCap_Con.add(
            model.Ceres_SCap[t-1]
            - model.Ceres3[t-1] - model.Ceres6[t-1] - model.Ceres9[t-1] - model.Ceres12[t-1] - model.Ceres15[t-1]
            + model.Earth3[t-4] + model.Earth6[t-7] + model.Earth9[t-10] + model.Earth12[t-13] + model.Earth15[t-15]
            == model.Ceres_SCap[t])
    elif t > 15:
        model.SCap_Con.add(
            model.Ceres_SCap[t]
            - model.Ceres3[t] - model.Ceres6[t] - model.Ceres9[t] - model.Ceres12[t] - model.Ceres15[t]
            + model.Earth3[t-3] + model.Earth6[t-6] + model.Earth9[t-9] + model.Earth12[t-12] + model.Earth15[t-15]
            == model.Ceres_SCap[t+1])
    elif t > 12:
        model.SCap_Con.add(
            model.Ceres_SCap[t]
            - model.Ceres3[t] - model.Ceres6[t] - model.Ceres9[t] - model.Ceres12[t] - model.Ceres15[t]
            + model.Earth3[t-3] + model.Earth6[t-6] + model.Earth9[t-9] + model.Earth12[t-12]
            == model.Ceres_SCap[t+1])
    elif t > 9:
        model.SCap_Con.add(
            model.Ceres_SCap[t]
            - model.Ceres3[t] - model.Ceres6[t] - model.Ceres9[t] - model.Ceres12[t] - model.Ceres15[t]
            + model.Earth3[t-3] + model.Earth6[t-6] + model.Earth9[t-9]
            == model.Ceres_SCap[t+1])
    elif t > 6:
        model.SCap_Con.add(
            model.Ceres_SCap[t]
            - model.Ceres3[t] - model.Ceres6[t] - model.Ceres9[t] - model.Ceres12[t] - model.Ceres15[t]
            + model.Earth3[t-3] + model.Earth6[t-6]
            == model.Ceres_SCap[t+1])
    elif t > 3:
        model.SCap_Con.add(
            model.Ceres_SCap[t]
            - model.Ceres3[t] - model.Ceres6[t] - model.Ceres9[t] - model.Ceres12[t] - model.Ceres15[t] 
            + model.Earth3[t-3]
            == model.Ceres_SCap[t+1])
    else:
        model.SCap_Con.add(
            model.Ceres_SCap[t]
            - model.Ceres3[t] - model.Ceres6[t] - model.Ceres9[t] - model.Ceres12[t] - model.Ceres15[t] 
            
            == model.Ceres_SCap[t+1])
    #####EARTH FUEL BALANCE
    if t == max(model.Time):
        model.FCap_Con.add(
            model.Earth_FCap[t-1]
            - model.Earth3[t-1]*model.Ef3[t-1] - model.Earth6[t-1]*model.Ef6[t-1] - model.Earth9[t-1]*model.Ef9[t-1]
            - model.Earth12[t-1]*model.Ef12[t-1] - model.Earth15[t-1]*model.Ef15[t-1]
            + model.Ceres3[t-4]*(model.max - model.Cf3[t-4]) 
            + model.Ceres6[t-7]*(model.max - model.Cf6[t-7]) 
            + model.Ceres9[t-10]*(model.max - model.Cf9[t-10])
            + model.Ceres12[t-13]*(model.max - model.Cf12[t-13])
            + model.Ceres15[t-16]*(model.max - model.Cf15[t-16])
            == model.Earth_FCap[t])
    elif t > 15:
        model.FCap_Con.add(
            model.Earth_FCap[t]
            - model.Earth3[t]*model.Ef3[t] - model.Earth6[t]*model.Ef6[t] - model.Earth9[t]*model.Ef9[t]
            - model.Earth12[t]*model.Ef12[t] - model.Earth15[t]*model.Ef15[t]
            + model.Ceres3[t-3]*(model.max - model.Cf3[t-3])
            + model.Ceres6[t-6]*(model.max - model.Cf6[t-6])
            + model.Ceres9[t-9]*(model.max - model.Cf9[t-9])
            + model.Ceres12[t-12]*(model.max - model.Cf12[t-12])
            + model.Ceres15[t-15]*(model.max - model.Cf15[t-15])
            == model.Earth_FCap[t+1])
    elif t > 12:
        model.FCap_Con.add(
            model.Earth_FCap[t]
            - model.Earth3[t]*model.Ef3[t] - model.Earth6[t]*model.Ef6[t] - model.Earth9[t]*model.Ef9[t]
            - model.Earth12[t]*model.Ef12[t] - model.Earth15[t]*model.Ef15[t]
            + model.Ceres3[t-3]*(model.max - model.Cf3[t-3])
            + model.Ceres6[t-6]*(model.max - model.Cf6[t-6])
            + model.Ceres9[t-9]*(model.max - model.Cf9[t-9])
            + model.Ceres12[t-12]*(model.max - model.Cf12[t-12])
            == model.Earth_FCap[t+1])
    elif t > 9:
        model.FCap_Con.add(
            model.Earth_FCap[t]
            - model.Earth3[t]*model.Ef3[t] - model.Earth6[t]*model.Ef6[t] - model.Earth9[t]*model.Ef9[t]
            - model.Earth12[t]*model.Ef12[t] - model.Earth15[t]*model.Ef15[t]
            + model.Ceres3[t-3]*(model.max - model.Cf3[t-3])
            + model.Ceres6[t-6]*(model.max - model.Cf6[t-6])
            + model.Ceres9[t-9]*(model.max - model.Cf9[t-9])
            == model.Earth_FCap[t+1])
    elif t > 6:
        model.FCap_Con.add(
            model.Earth_FCap[t]
            - model.Earth3[t]*model.Ef3[t] - model.Earth6[t]*model.Ef6[t] - model.Earth9[t]*model.Ef9[t]
            - model.Earth12[t]*model.Ef12[t] - model.Earth15[t]*model.Ef15[t]
            + model.Ceres3[t-3]*(model.max - model.Cf3[t-3])
            + model.Ceres6[t-6]*(model.max - model.Cf6[t-6])
            == model.Earth_FCap[t+1])
    elif t > 3:
        model.FCap_Con.add(
            model.Earth_FCap[t]
            - model.Earth3[t]*model.Ef3[t] - model.Earth6[t]*model.Ef6[t] - model.Earth9[t]*model.Ef9[t]
            - model.Earth12[t]*model.Ef12[t] - model.Earth15[t]*model.Ef15[t]
            + model.Ceres3[t-3]*(model.max - model.Cf3[t-3])
            == model.Earth_FCap[t+1])
    else:
        model.FCap_Con.add(
            model.Earth_FCap[t]
            - model.Earth3[t]*model.Ef3[t] - model.Earth6[t]*model.Ef6[t] - model.Earth9[t]*model.Ef9[t]
            - model.Earth12[t]*model.Ef12[t] - model.Earth15[t]*model.Ef15[t]
            
            == model.Earth_FCap[t+1])
    
    #####CERES FUEL BALANCE
    if t == max(model.Time):
        model.FCap_Con.add(
            model.Ceres_FCap[t-1]
            - model.Ceres3[t-1]*model.max - model.Ceres6[t-1]*model.max - model.Ceres9[t-1]*model.max
            - model.Ceres12[t-1]*model.max - model.Ceres15[t-1]*model.max
            - model.Ceres_FCap[t]
            ==-model.fuelprod[t])

    elif t > 9:
        model.FCap_Con.add(
            model.Ceres_FCap[t]
            - model.Ceres3[t]*model.max - model.Ceres6[t]*model.max - model.Ceres9[t]*model.max
            - model.Ceres12[t]*model.max - model.Ceres15[t]*model.max
            - model.Ceres_FCap[t+1]
            ==-model.fuelprod[t])
    elif t > 6:
        model.FCap_Con.add(
            model.Ceres_FCap[t]
            - model.Ceres3[t]*model.max - model.Ceres6[t]*model.max - model.Ceres9[t]*model.max
            - model.Ceres12[t]*model.max - model.Ceres15[t]*model.max
            - model.Ceres_FCap[t+1]
            ==-model.fuelprod[t])
    elif t > 3:
        model.FCap_Con.add(
            model.Ceres_FCap[t]
            - model.Ceres3[t]*model.max - model.Ceres6[t]*model.max - model.Ceres9[t]*model.max
            - model.Ceres12[t]*model.max - model.Ceres15[t]*model.max
            - model.Ceres_FCap[t+1]
            ==-model.fuelprod[t])
    else:
        model.FCap_Con.add(
            model.Ceres_FCap[t]
            - model.Ceres3[t]*model.max - model.Ceres6[t]*model.max - model.Ceres9[t]*model.max
            - model.Ceres12[t]*model.max - model.Ceres15[t]*model.max
            - model.Ceres_FCap[t+1]
            ==-model.fuelprod[t])

    #model.ECheck.add(model.Ceres3[t] + model.Ceres6[t] + model.Ceres9[t] <= model.Ceres_SCap[t])
    #model.ECheck.add(model.Earth3[t] + model.Earth6[t] + model.Earth9[t] <= model.Earth_SCap[t])
    #model.ECheck.add(model.Earth_SCap[t] <= 1)
    #model.ECheck.add(model.Ceres_SCap[t] <= 1)
    #model.ECheck.add(model.Earth_FCap[t] <= 1000000) #####DING
    #model.ECheck.add(model.Ceres_FCap[t] <= 1000000)
    #model.ECheck.add(model.Earth3[t] <= 1)
    #model.ECheck.add(model.Earth6[t] <= 1)
    #model.ECheck.add(model.Earth9[t] <= 1)
    #model.ECheck.add(model.Ceres3[t] <= 1)
    #model.ECheck.add(model.Ceres6[t] <= 1)
    #model.ECheck.add(model.Ceres9[t] <= 1)
model.Initial_Cap_Con.add(model.Ceres_FCap[0] == 0)#100000)
#may want to consider giving earth some initial fuel
model.Initial_Cap_Con.add(model.Earth_FCap[0] == 0)
#start the ships on Ceres, may want to change this later
model.Initial_Cap_Con.add(model.Ceres_SCap[0] == model.Ships)
model.Initial_Cap_Con.add(model.Earth_SCap[0] == 0)
solver = pyomo.opt.SolverFactory('cplex')

results = solver.solve(model, tee=True, keepfiles=True)

#really fucking crude excel drop in, don't judge me
wb = xw.Book(r'C:\Users\DAnderson\Documents\Grad School\Asteroid\toy_results.xlsx')
try:
    wb.sheets.add('results')
except:
    pass
sht = wb.sheets('results')
rowiter =0
sht.range('A'+str(1)+':'+'P'+str(1)).value = ['Time','Earth_Fuel','Ceres_Fuel',' ','Earth_Ships','Earth_3_Depart','Earth_6_Depart','Earth_9_Depart','Earth_12_Depart','Earth_15_Depart',' ','Ceres_Ships','Ceres_3_Depart','Ceres_6_Depart','Ceres_9_Depart','Ceres_12_Depart','Ceres_15_Depart']

for t in model.Time:
    sht.range('A'+str(t+2)+':'+'K'+str(t+2)).value = [t, model.Earth_FCap[t].value, model.Ceres_FCap[t].value,' ',model.Earth_SCap[t].value,model.Earth3[t].value, model.Earth6[t].value, model.Earth9[t].value, model.Earth12[t].value, model.Earth15[t].value,' ',model.Ceres_SCap[t].value, model.Ceres3[t].value, model.Ceres6[t].value, model.Ceres9[t].value, model.Ceres12[t].value, model.Ceres15[t].value]

    
