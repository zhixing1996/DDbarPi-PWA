import os, yaml, json
cur_dir = os.path.abspath(os.path.dirname('__file__'))
from .tools import sort_result

def deploy_scan(path, mass, width, decimal, conf, resonance_scan, resonances, f_res_base, scan_list_size):
    path_root = path
    path += resonance_scan + '/'
    if not os.path.exists(path): os.makedirs(path)
    mass_min, mass_max, mass_N = mass
    width_min, width_max, width_N = width
    mass_step = (mass_max - mass_min)/mass_N
    width_step = (width_max - width_min)/width_N
    decimal = 1/decimal
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
            scan_path = path + str(int(m * decimal)) + '_' + str(int(w * decimal)) + '/'
            res_base[resonance_scan]['m0'] = m
            res_base[resonance_scan]['g0'] = w
            os.system('cd ' + path + ' && mkdir -p ' + path + str(int(m * decimal)) + '_' + str(int(w * decimal)) + '/')
            conf['particle']['$include'] = scan_path + 'Resonances.yml'
            with open(scan_path + 'Resonances.yml', 'w') as f:
                yaml.dump(res_base, f)
            with open(scan_path + 'config.yml', 'w') as f:
                yaml.dump(conf, f)
            os.system('cp ' + cur_dir + '/scripts/fit.py ' + scan_path)
            init_params = generate_init_params(path_root, resonance_scan, m, w)
            with open(scan_path + 'init_params.json', 'w') as f:
                json.dump(init_params, f, indent = 2)
            scan_list.append(scan_path)
    scan_list_group = split_list(scan_list, scan_list_size)
    return scan_list_group

def execute_scan(scan_list, search_step, converge_number, projection = 'BD', nbins = 400):
    for scan in scan_list:
        os.system('mkdir -p ' + scan + 'fit_results')
        for i in range(1):
            os.system('cd ' + scan + ' && python ' + scan + 'fit.py --config ' + scan + 'config.yml --init_params ' + scan + 'init_params.json' + ' -r ' + projection + ' -b ' + str(nbins))
            os.system('mv ' + scan + 'final_params.json ' + scan + 'fit_results/final_params_' + str(i + 1) + '.json')
        # solution = sort_result(scan + 'fit_results', search_step, converge_number)
        # os.system('mv ' + scan + 'fit_results/final_params_' + str(solution) + '.json ' + scan + 'final_params.json')
        os.system('mv ' + scan + 'fit_results/final_params_1.json ' + scan + 'final_params.json')
        os.system('rm -rf ' + scan + 'fit_results')

def generate_init_params(path, resonance_scan, m, w):
    with open(path + 'final_params.json') as fp:
        params = json.load(fp)
    params['value'][resonance_scan + '_mass'] = m
    params['value'][resonance_scan + '_width'] = w
    return params

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
