import design

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
    race_1 = design.Race('207883','10+km+TC')
    race_2 = design.Race('205515','10+Km+Route')
    print(sort_races(None,'meantime',race_1,race_2))
