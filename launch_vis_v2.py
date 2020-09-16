from postprocess3 import PostProcess
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

run = PostProcess('sens_900_3000.0', path='solar-elec-sens')
sch = run.get_launch_schedule()
sort_idx = sch['Qty'].sort_values(ascending=False).index

print(run.n)
print(run.s.max())

print(sch[['Time', 'Qty']])

run.f['Mars'].plot(color='maroon', label='Mars')
run.f['Ceres'].plot(color='olive', label='Ceres')
run.f['Earth'].plot(color='blue', label='Earth')
plt.xlim(xmin=0, xmax=run.T)
plt.ylabel('fuel storage (kg)')
plt.xlabel('time (d)')
plt.show()

stcargs = {'markeredgecolor': 'black', 'markeredgewidth': 1.0}
dynargs = {
    ('Mars', 'Ceres'):  {'color': 'lightcoral',     'marker': '^'},
    ('Ceres', 'Mars'):  {'color': 'lightcoral',     'marker': 'v'},
    ('Earth', 'Ceres'): {'color': 'gold',  'marker': '^'},
    ('Ceres', 'Earth'): {'color': 'gold',  'marker': 'v'},
    ('Earth', 'Mars'):  {'color': 'deepskyblue', 'marker': '^'},
    ('Mars', 'Earth'):  {'color': 'deepskyblue', 'marker': 'v'}
}
ms = 8

plt.figure(num=None, figsize=(15, 9), dpi=80, facecolor='w', edgecolor='k')


plt.subplot(5, 1, 1)

dist_mc = run.get_dist_between('Mars', 'Ceres')
dist_ec = run.get_dist_between('Earth', 'Ceres')
dist_me = run.get_dist_between('Mars', 'Earth')

dist_mc.plot(color='maroon', label='Mars-Ceres Distance')
#dist_ec.plot(color='olive', label='Earth-Ceres Distance')
#dist_me.plot(color='blue', label='Mars-Earth Distance')

for idx in sort_idx:
    plt.plot(sch.at[idx, 'Time'], sch.at[idx, 'Dist'],
#             markersize=ms*(sch.at[idx, 'Qty']) ** 0.5,
             markersize=ms,
             **stcargs,
             **dynargs[tuple(sch.loc[idx, ['To', 'From']].tolist())]
    )
labels = [item.get_text() for item in plt.gca().get_xticklabels()]
empty_string_labels = ['']*len(labels)
plt.gca().set_xticklabels(empty_string_labels)

# for sake of legend
plt.scatter(None, None, **dynargs[('Mars', 'Ceres')],  label='Mars to Ceres')
plt.scatter(None, None, **dynargs[('Ceres', 'Mars')],  label='Ceres to Mars')
plt.scatter(None, None, **dynargs[('Earth', 'Ceres')], label='Earth to Ceres')
plt.scatter(None, None, **dynargs[('Ceres', 'Earth')], label='Ceres to Earth')
plt.scatter(None, None, **dynargs[('Mars', 'Earth')],  label='Mars to Earth')
plt.scatter(None, None, **dynargs[('Earth', 'Mars')],  label='Earth to Mars')


plt.xlim(xmin=0, xmax=run.T)
plt.ylabel('distance (km)')
plt.legend(ncol=3, bbox_to_anchor=(0.73, 1.25))

plt.subplot(5, 1, 2)
for idx in sort_idx:
    plt.plot(sch.at[idx, 'Time'], sch.at[idx, 'Qty'],
             markersize=ms,
             **stcargs,
             **dynargs[tuple(sch.loc[idx, ['To', 'From']].tolist())]
    )
labels = [item.get_text() for item in plt.gca().get_xticklabels()]
empty_string_labels = ['']*len(labels)
plt.gca().set_xticklabels(empty_string_labels)
plt.ylabel('# ships')


plt.subplot(5, 1, 3)
for idx in sort_idx:
    plt.plot(sch.at[idx, 'Time'], sch.at[idx, 'Cost'],
             markersize=ms,
             #markersize=ms*(sch.at[idx, 'Qty']) ** 0.5,
             **stcargs,
             **dynargs[tuple(sch.loc[idx, ['To', 'From']].tolist())]
    )
plt.xlim(xmin=0, xmax=run.T)

plt.gca().set_xticklabels(empty_string_labels)
plt.ylim(ymin=0, ymax=run.ship.capacity)
plt.ylabel('fuel cost (kg)')


plt.subplot(5, 1, 4)
for idx in sort_idx:
    plt.plot(sch.at[idx, 'Time'], sch.at[idx, 'Delta-v'],
             markersize=ms,
             #markersize=ms*(sch.at[idx, 'Qty']) ** 0.5,
             **stcargs,
             **dynargs[tuple(sch.loc[idx, ['To', 'From']].tolist())]
    )
plt.xlim(xmin=0, xmax=run.T)
plt.gca().set_xticklabels(empty_string_labels)
plt.ylim(ymin=0, ymax=15)
plt.ylabel('Δv (km/s)')


plt.subplot(5, 1, 5)
for idx in sort_idx:
    plt.plot(sch.at[idx, 'Time'], sch.at[idx, 'Route'],
             markersize=ms,
             #markersize=ms*(sch.at[idx, 'Qty']) ** 0.5,
             **stcargs,
             **dynargs[tuple(sch.loc[idx, ['To', 'From']].tolist())]
    )

plt.xlim(xmin=0, xmax=run.T)
plt.ylim(ymin=0, ymax=1500)
plt.ylabel('trip duration (d)')
plt.xlabel('time (d)')

plt.show()