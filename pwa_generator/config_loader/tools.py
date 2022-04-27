from itertools import combinations
from copy import deepcopy
import os, yaml

def print_sep(mark, N):
    print(mark * N)

def combination_generator(resonances):
    combos = []
    if len(resonances) == 1:
        for combo in combinations(resonances, 1): combos.append(combo)
    else:
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
        for combo_veto in combination_veto:
            if len(combo_veto) == len(combo):
                for res in combo_veto:
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
    conf_tmp['data']['data'][0] = conf_tmp['data']['data'][0].replace('sample', str(sample))
    conf_tmp['data']['phsp'][0] = conf_tmp['data']['phsp'][0].replace('sample', str(sample))
    conf_tmp['data']['bg'][0] = conf_tmp['data']['bg'][0].replace('sample', str(sample))
    conf_tmp['data']['bg_weight'][0] = conf_tmp['data']['bg_weight'][0].replace('sample', str(sample))
    del(conf_tmp['data']['sample'])
    conf['data'] = conf_tmp['data']
    conf['decay'] = conf_tmp['decay']
    conf_tmp['particle']['R_BD'] = [res for res in combo if res != 'PHSP']
    phsp = [res.lower() for res in combo if res == 'PHSP']
    if phsp != []: conf_tmp['particle']['R_BD'].append(phsp[0])
    conf_tmp['particle']['R_CD'] = [res + 'p' for res in combo if res != 'PHSP']
    conf_tmp['particle']['R_BC'] = [res for res in combo if res != 'PHSP' and res[0] != 'D']
    conf['particle'] = conf_tmp['particle']
    conf['constrains'] = conf_tmp['constrains']
    return conf

def sort_result(path, search_step, converge_number):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    file_num = len(os.listdir(path))
    results = {
        'index': [],
        'NLL': [],
    }
    index, NLL = [], []
    for count in range(file_num):
        f_name = path + '/final_params_' + str(count + 1) + '.json'
        with open(f_name) as f:
            result = yaml.load(f, yaml.FullLoader)
        if result['status']['success'] != True: continue
        index.append(count + 1)
        NLL.append(result['status']['NLL'])
    results['index'] = index
    results['NLL'] = NLL
    pd_results = pd.DataFrame(results)
    sorted_results = pd_results.sort_values(by = 'NLL')
    NLL_min = min(sorted_results['NLL'])
    NLL_max = max(sorted_results['NLL'])
    bins = list(np.arange(int(NLL_min) - 1., int(NLL_max) + 1., search_step))
    segments = pd.cut(sorted_results['NLL'], bins)
    counts = pd.value_counts(segments, sort = False)
    converge_range = ''
    for idx in counts.index:
        if counts[idx] >= converge_number:
            converge_range = idx
            break
    converge_min, converge_max = map(float, str(converge_range).strip().strip('(').strip(')').strip('[').strip(']').replace(',', '').split())
    print('Sorted_results: \n', sorted_results, converge_min, converge_max)
    print('Counted results:\n', counts)
    solutions = solution_filter(sorted_results, converge_max, converge_min)
    solution = sorted_results['index'][solutions.index[0]]
    print('solution {}, converged from {}/{}: \n'.format(str(solution), converge_number, file_num))
    return solution

def solution_filter(results, max, min):
    return results[(results.NLL > min) & (results.NLL < max)]

def conf_draw_generator(sample, config, combo):
    conf = {}
    conf = conf_generator(sample, config, combo)
    conf['plot'] = config['plot']
    return conf
