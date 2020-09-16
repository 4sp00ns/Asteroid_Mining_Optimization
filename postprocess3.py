import os
import pandas as pd
import json
import math
import matplotlib.pyplot as plt

from rocketship import RocketShip

class PostProcess(object):

    def __init__(self, uid, path=os.getcwd()):
        self.uid = uid
        self.path = path

        self.load_params()
        self.load_posvel()
        self.load_deltav()

        self.load_f()
        self.load_d()
        self.load_c()
        self.load_p()
        self.load_q()
        self.load_s()
        self.load_x()
        self.load_y()

    ### LOAD ###

    def get_path(self, filename):
        return os.path.join(self.path, filename)

    def load_params(self):
        filename = self.get_path('params_{}.json'.format(str(self.uid)))
        with open(filename) as json_data:
            params = json.load(json_data)
        self.z = params['z']
        self.z_lb = params['z_lb']
        self.z_ub = params['z_ub']
        self.T = params['T']
        self.tau = params['tau']
        self.gamma = params['gamma']
        self.n = params['num_ships']
        self.ship = RocketShip(mass=params['ship_mass'],
                               capacity=params['ship_capacity'],
                               thrust_scale =params['ship_thrust_scale'])
        self.s_nodes = params['s_nodes']
        self.d_nodes = params['d_nodes']
        self.routes = params['routes']
        self.gurobi_opts = params['gurobi_opts']

    def load_posvel(self):
        filename = os.path.join('datasets', 'posvel_{}.csv')
        self.posvel = {}
        for i in self.d_nodes + self.s_nodes:
            self.posvel[i] = pd.read_csv(filename.format(i))
            self.posvel[i].drop('Unnamed: 8', axis=1, inplace=True)
            self.posvel[i].columns = map(str.strip, self.posvel[i].columns)

    def load_deltav(self):
        def parse_header(col):
            (i, j, r) = col.split(',')
            return (str(i), str(j), int(r))
        filename = os.path.join('datasets', 'revamp_deltav.csv')
        self.deltav = pd.read_csv(filename, index_col=0)
        self.deltav.columns = list(map(parse_header, self.deltav.columns))

    def load_c(self):
        def parse_header(col):
            (i, j, r) = col.split(',')
            return (str(i), str(j), int(r))
        filename = self.get_path('c_{}.csv'.format(str(self.uid)))
        self.c = pd.read_csv(filename, index_col=0)
        self.c.columns = list(map(parse_header, self.c.columns))

    def load_p(self):
        def parse_header(col):
            (i, j, r) = col.split(',')
            return (str(i), str(j), int(r))
        filename = self.get_path('p_{}.csv'.format(str(self.uid)))
        self.p = pd.read_csv(filename, index_col=0)
        self.p.columns = list(map(parse_header, self.p.columns))

    def load_q(self):
        def parse_header(col):
            (i, j, r) = col.split(',')
            return (str(i), str(j), int(r))
        filename = self.get_path('q_{}.csv'.format(str(self.uid)))
        self.q = pd.read_csv(filename, index_col=0)
        self.q.columns = list(map(parse_header, self.q.columns))

    def load_x(self):
        def parse_header(col):
            (i, j, r) = col.split(',')
            return (str(i), str(j), int(r))
        filename = self.get_path('x_{}.csv'.format(str(self.uid)))
        self.x = pd.read_csv(filename , index_col=0)
        try:
            self.x.drop('t', axis=0, inplace=True)
        except:
            None
        for col in self.x.columns:
            if col.startswith('Unnamed'):
                self.x.drop(col, axis=1, inplace=True)
        self.x.columns = list(map(parse_header, self.x.columns))
        self.x = self.x.fillna(0)

    def load_y(self):
        filename = self.get_path('y_{}.csv'.format(str(self.uid)))
        self.y = pd.read_csv(filename, index_col=0)

    def load_f(self):
        filename = self.get_path('f_{}.csv'.format(str(self.uid)))
        self.f = pd.read_csv(filename, index_col=0)

    def load_d(self):
        filename = self.get_path('d_{}.csv'.format(str(self.uid)))
        self.d = pd.read_csv(filename, index_col=0)

    def load_s(self):
        filename = self.get_path('s_{}.csv'.format(str(self.uid)))
        self.s = pd.read_csv(filename, index_col=0)

    ### ANALYSIS ###

    def get_dist_between(self, i, j):
        dxyz = self.posvel[i][['X', 'Y', 'Z']] - self.posvel[j][['X', 'Y', 'Z']]
        dxyz2 = dxyz.apply(lambda v: v ** 2)
        return dxyz2.sum(axis=1).apply(lambda v: v ** 0.5)

    def get_launches_by_dist(self, i, j):
        launches = []
        for t in self.x.index:
            for col in self.x.columns:
                if self.x.at[t, col] > 0 and col[:2] == (i, j):
                    launches.append((t, *col, self.x.at[t, col]))
        return launches

    def get_launches_by_route(self):
        df = pd.DataFrame()
        for r in self.routes:
            df[r] = sum(self.x[col]
                        for col in self.x.columns if col[-1] == r)
        return df.sum(axis=0)

    def get_launch_schedule(self):
        df = pd.DataFrame([
            [t, *col, self.x.at[t, col], self.c.at[t, col], self.q.at[t, col],
             self.p.at[t, col], self.deltav.at[t, col],
             self.get_dist_between(*col[0:2]).loc[t]]
            for t in self.x.index for col in self.x.columns
            if self.x.at[t, col] > 10e-3
        ], columns=['Time', 'From', 'To', 'Route', 'Qty', 'Cost', 'Consumed',
                    'Delivered', 'Delta-v', 'Dist'])
        return df
