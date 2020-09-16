from math import exp

class RocketShip(object):
    """
    A variation of the SpaceX transport ship.
    """

    g = 0.00980665 # km / s^2
    impulse = 465

    def __init__(self, mass, capacity, thrust_scale):
        self.mass = mass # kg
        self.capacity = capacity # kg
        self.thrust_scale = thrust_scale # unitless

    def vel_to_fuel_full(self, dv):
        m0 = self.mass + self.capacity # kg
        ve = self.impulse * self.g * self.thrust_scale
        return (1 - exp(-dv / ve)) * m0

    def vel_to_fuel_empty(self, dv):
        mf = self.mass
        ve = self.impulse * self.g * self.thrust_scale
        #print(dv,ve,mf)
        return (exp(dv / ve) - 1) * mf
