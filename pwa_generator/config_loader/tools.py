from itertools import combinations
from copy import deepcopy

def combination_generator(resonances):
    combos = []
    for i in range(len(resonances) + 1):
        if i < 2: continue
        else:
            for combo in combinations(resonances, i): combos.append(combo)
    return combos

def combination_filter(resonance_main, combination_veto, combos):
    combos_ret = []
    for combo in combos:
        check_list = []
        for res in resonance_main:
            if res in combo: check_list.append(True)
            else: check_list.append(False)
        if len(combination_veto) == len(combo):
            for res in combination_veto:
                if res in combo: check_list.append(False)
        if all(check_list): combos_ret.append(combo)
    return combos_ret

def paste(combo):
    ret = ''
    combo = list(combo)
    for i in range(len(combo) - 1):
        ret += str(combo[i]) + '_'
    ret += str(combo[-1])
    return ret

def conf_generator(sample, config, combo):
    conf = {}
    conf_tmp = deepcopy(config)
    conf_tmp['data']['data'][0].replace('sample', str(sample))
    conf_tmp['data']['phsp'][0].replace('sample', str(sample))
    conf_tmp['data']['bg'][0].replace('sample', str(sample))
    conf_tmp['data']['bg_weight'][0].replace('sample', str(sample))
    del(conf_tmp['data']['sample'])
    conf['data'] = conf_tmp['data']
    conf['decay'] = conf_tmp['decay']
    conf_tmp['particle']['R_BD'] = [res for res in combo if res != 'PHSP']
    conf_tmp['particle']['R_CD'] = [res + 'p' for res in combo if res != 'PHSP']
    conf_tmp['particle']['R_BC'] = [res.lower() for res in combo if res == 'PHSP']
    conf['particle'] = conf_tmp['particle']
    conf['constrains'] = conf_tmp['constrains']
    return conf
