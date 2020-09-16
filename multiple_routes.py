def run_example2():
    import numpy as np
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D

    import matplotlib.pyplot as plt
    from pykep import epoch, DAY2SEC, AU, MU_SUN, lambert_problem
    from pykep.planet import jpl_lp, gtoc7
    from pykep.orbit_plots import plot_planet, plot_lambert

    mpl.rcParams['legend.fontsize'] = 10

    fig = plt.figure()
    axis = fig.gca(projection='3d')

    t0 = 365 * 25 + 7 + 0.5
    t1 = epoch(t0)
    t2 = epoch(t0 + 120)
    t3 = epoch(t0 + 240)
    t4 = epoch(t0 + 860)

    dt2 = (t2.mjd2000 - t1.mjd2000) * DAY2SEC
    dt3 = (t3.mjd2000 - t1.mjd2000) * DAY2SEC
    dt4 = (t4.mjd2000 - t1.mjd2000) * DAY2SEC

    axis.scatter([0], [0], [0], color='y')

    earth = jpl_lp('earth')
    earth.name = 'Earth on'
    plot_planet(
        earth, t0=t1, color='gray', legend=True, units=AU, ax=axis)
    r0, v0 = earth.eph(t1)

    ceres = gtoc7(1)
    ceres.name = 'Ceres Arrival:'
    plot_planet(
        ceres, t0=t2, color='red', legend=True, units=AU, ax=axis)

    plot_planet(
        ceres, t0=t3, color='purple', legend=True, units=AU, ax=axis)

    plot_planet(
        ceres, t0=t4, color='blue', legend=True, units=AU, ax=axis)

    ceres.name = 'Ceres on'
    plot_planet(
        ceres, t0=t1, color='black', legend=True, units=AU, ax=axis)


    rf, vf = ceres.eph(t2)
    l = lambert_problem(r0, rf, dt2, MU_SUN)
    plot_lambert(l, color='red', units=AU, ax=axis)

    rf, vf = ceres.eph(t3)
    l = lambert_problem(r0, rf, dt3, MU_SUN)
    plot_lambert(l, color='purple', units=AU, ax=axis)

    rf, vf = ceres.eph(t4)
    l = lambert_problem(r0, rf, dt4, MU_SUN)
    plot_lambert(l, color='darkblue', units=AU, ax=axis)
    plot_lambert(l, sol=1, color='blue', units=AU, ax=axis)
    plot_lambert(l, sol=2, color='lightblue', units=AU, ax=axis)


    axis.set_xlabel('x (AU)')
    axis.set_ylabel('y (AU)')
    axis.set_zlabel('z (AU)')
    plt.show()

if __name__ == '__main__':
    run_example2()
