import os, yaml
cur_dir = os.path.abspath(os.path.dirname('__file__'))
from .tools import sort_result

def deploy_scan(path, mass, width, precision, conf, resonance_scan, resonances, f_res_base):
    path += resonance_scan + '/'
    if not os.path.exists(path): os.makedirs(path)
    mass_min, mass_max, mass_N = mass
    width_min, width_max, width_N = width
    mass_step = (mass_max - mass_min)/mass_N
    width_step = (width_max - width_min)/width_N
    precision = 1/precision
    mass_sets = [mass_min + i * mass_step for i in range(mass_N + 1)]
    width_sets = [width_min + i * width_step for i in range(width_N + 1)]
    res_base = {}
    with open(f_res_base) as f:
        base = yaml.load(f, yaml.FullLoader)
    for res in resonances:
        res_base[res] = base[res]
    os.system('rm -rf ' + path + ' && mkdir -p ' + path)
    scan_list = []
    for m in mass_sets:
        for w in width_sets:
            print('Deploying {}/{} combo...'.format(m, w))
            scan_path = path + str(int(m * precision)) + '_' + str(int(w * precision)) + '/'
            res_base[resonance_scan]['m0'] = m
            res_base[resonance_scan]['g0'] = w
            os.system('cd ' + path + ' && mkdir -p ' + path + str(int(m * precision)) + '_' + str(int(w * precision)) + '/')
            conf['particle']['$include'] = scan_path + 'Resonances.yml'
            with open(scan_path + 'Resonances.yml', 'w') as f:
                yaml.dump(res_base, f)
            with open(scan_path + 'config.yml', 'w') as f:
                yaml.dump(conf, f)
            os.system('cp ' + cur_dir + '/scripts/fit.py ' + scan_path)
            scan_list.append(scan_path)
    return scan_list

def execute_scan(scan_list, path, search_step, converge_number):
    for scan in scan_list:
        os.system('mkdir -p ' + scan + 'fit_results')
        for i in range(10):
            os.system('cd ' + scan + ' && python ' + scan + 'fit.py --config ' + scan + 'config.yml --init_params ' + path + 'final_params.json')
            os.system('mv ' + scan + 'final_params.json ' + scan + 'fit_results/final_params_' + str(i + 1) + '.json')
        solution = sort_result(scan + 'fit_results', search_step, converge_number)
        os.system('mv ' + scan + 'fit_results/final_params_' + str(solution) + '.json ' + scan + 'final_params.json')
        os.system('rm -rf ' + scan + 'fit_results')
