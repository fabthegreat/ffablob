import design
#import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
#from numpy.random import rand


def std_stat_table(races=[]):
    """ create table of statistic values from list of races
    """
    if races:
        for race in races:
            race.create_race_stats('meantime')
            race.create_race_stats('mediantime')


def sort_races(sample_size=None,sort_key='meantime',*races):
    """ sort races about created statistics 
    """
    cmp_list = []
    for r in races:
        r.create_race_stats(sort_key,sample_size)

    if sample_size is None:
        postfix = ''
    else:
        postfix = '_' + str(sample_size)

    return sorted(races,key=lambda x: x.race_stats[sort_key + postfix].time.total_seconds())


if __name__ == '__main__':
    a = rand(100)
    b = rand(100)
#    plt.scatter(a, b)
#    plt.savefig('/home/ftg/python/ffablob/foo.png')
#    race_1 = design.Race('207883','10+km+TC')
#    race_2 = design.Race('205515','10+Km+Route')
#    print(sort_races(None,'meantime',race_1,race_2))

#    std_stat_table([race_1,race_2])
