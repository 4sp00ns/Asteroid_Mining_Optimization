from postprocess3 import PostProcess
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import pandas as pd
import numpy as np

"""
path = 'spacex_thrust'
uids = ['spacex' + str(i) for i in range(7, 12)]

path = 'thrust_sens_s5'
uids = ['thrust' + str(i) for i in range(12, 19)]
"""

path = 'min_max_prod'
uids = ['gamma' + str(i) for i in [0, 1000, 2000, 2500, 3000, 3250, 3500, 3750, 4000, 4250, 4500]]

run = {}
for uid in uids:
    run[uid] = PostProcess(uid, path=path)

"""
for uid in uids:
    print(run[uid].get_z(), len(run[uid].get_launches_all()))
"""


plt.figure(num=None, figsize=(15, 9), dpi=100, facecolor='w', edgecolor='k')

major = MultipleLocator(5)
for i, k in enumerate(run):

    plt.subplot(1, len(run), i+1)

    run[k].get_launches_by_route().plot(kind='barh', width=.80)

    plt.ylabel('\nDurations of Route Options (d)')

    plt.xlim(xmax=7)
#    plt.ylim(ymin=1.5, ymax=14.5)

    ax = plt.gca()
    if i == 0:
        plt.ylabel('\nDurations of Route Options (d)')
    else:
        ax.yaxis.set_visible(False)
    ax.xaxis.set_major_locator(major)

    plt.xlabel('Launches for\n{} Thrusters\n'.format(run[k].ship.thrust_scale))


plt.savefig('cts.png')
plt.show()



