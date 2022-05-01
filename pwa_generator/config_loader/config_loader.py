from .base_config import BaseConfig
from .tools import (
    combination_generator, 
    combination_filter, 
    conf_generator, 
    paste, 
    print_sep, 
    sort_result, 
    conf_draw_generator
)
import os, yaml, time
from .scan import deploy_scan, execute_scan
from pwa_generator.scan_seq import scan_seq
cur_dir = os.path.abspath(os.path.dirname('__file__'))

class ConfigLoader(BaseConfig):
    """ class for loading config.conf """

    def __init__(self, file_name, search_step = 1., converge_number = 3, scan_decimal = 0.0001, share_dict = None):
        if share_dict is None:
            share_dict = {}
        super().__init__(file_name, share_dict)
        self.combos = self.generate_combination()
        self.search_step = search_step
        self.converge_number = converge_number
        self.scan_decimal = scan_decimal

    def generate_combination(self):
        if self.config['combination']['combination_focus'] != []: ret = [tuple(self.config['combination']['combination_focus'])]
        else:
            ret = combination_filter(
                    self.config['combination']['resonance_main'],
                    self.config['combination']['combination_veto'],
                    combination_generator(self.config['combination']['resonance'])
                  )
        return ret

    def generate_conf(self):
        print_sep('|', 50)
        print('Generating configuration files...')
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            for combo in self.combos:
                print('Proceeding {} combo...'.format(paste(combo)))
                time.sleep(1)
                path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/'
                if not os.path.exists(path): os.makedirs(path)
                with open(path + 'config.yml', 'w') as f:
                    yaml.dump(conf_generator(sample, self.config, combo), f)

    def generate_conf_draw(self):
        print_sep('|', 50)
        print('Generating drawing configuration files...')
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            for combo in self.combos:
                print('Proceeding {} combo...'.format(paste(combo)))
                time.sleep(1)
                path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/'
                if not os.path.exists(path): os.makedirs(path)
                with open(path + 'config_draw.yml', 'w') as f:
                    yaml.dump(conf_draw_generator(sample, self.config, combo), f)

    def generate_job(self):
        print_sep('|', 50)
        print('Generating gpu jobs...')
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            for combo in self.combos:
                print('Proceeding {} combo...'.format(paste(combo)))
                time.sleep(1)
                path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/'
                os.system('cp ' + cur_dir + '/scripts/fit.py ' + path)
                os.system('mkdir -p ' + path + '/run && cp ' + cur_dir + '/scripts/submit_RES_gpu.sh ' + path + '/run/submit_' + paste(combo) + '_gpu.sh')
                os.system('sed -i \'s/RES/' + paste(combo) + '/g\' ' + path + '/run/submit_' + paste(combo) + '_gpu.sh')
                os.system('sed -i \'s/PATH/' + path.replace('/', '\/') + '/g\' ' + path + '/run/submit_' + paste(combo) + '_gpu.sh')

    def test_job(self):
        flag = input('Do your want to proceed job testing? / [yes]/[no]')
        if flag == 'no':
            print('Now exit...')
            exit()
        elif flag == 'yes':
            path = cur_dir + '/base_solution/' + str(self.config['data']['sample'][0]) + '/' + paste(self.combos[0]) + '/'
            os.system('cd ' + path + ' && python fit.py')
        else:
            print('Please enter [yes] or [no]')
            exit()

    def submit_job(self):
        print_sep('|', 50)
        print('Submitting gpu jobs...')
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            for combo in self.combos:
                print('Proceeding {} combo...'.format(paste(combo)))
                time.sleep(1)
                path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/run'
                os.system('cd ' + path + ' && sbatch submit_' + paste(combo) + '_gpu.sh')

    def find_solution(self):
        print_sep('|', 50)
        print('Finding solutions...')
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            for combo in self.combos:
                print('Proceeding {} combo...'.format(paste(combo)))
                time.sleep(1)
                path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/fit_result/'
                solution = sort_result(path, self.search_step, self.converge_number)
                os.system('rm -rf ' + path + 'final_params.json')
                os.system('cp ' + path + 'final_params_' + str(solution) + '.json ' + path + '../final_params.json')

    def draw_result(self):
        print_sep('|', 50)
        print('Drawing solutions...')
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            for combo in self.combos:
                print('Proceeding {} combo...'.format(paste(combo)))
                time.sleep(1)
                path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/'
                os.system('python ' + path + 'fit.py --config ' + path + 'config_draw.yml --init_params ' + path + 'final_params.json')
                os.system('rm ' + path + 'figure -rf')
                os.system('mv figure ' + path + ' && mv final_params.json ' + path)

    def scan(self):
        print_sep('|', 50)
        print('Scanning mass and width of {}...'.format(self.config['scan']['resonance']))
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            if len(self.combos) != 1:
                print('You have to focus on one combo to perform mass and width scan, please set it!')
                exit()
            combo = self.combos[0]
            temp_res = self.config['scan']['resonance']
            if not (temp_res in combo or temp_res[:-1] in combo):
                print('The resonance you scan is not in the combo you focus on!')
                exit()
            print('Proceeding {} combo...'.format(paste(combo)))
            time.sleep(1)
            print('Deploying {}...'.format(self.config['scan']['resonance']))
            time.sleep(1)
            path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/'
            conf = conf_generator(sample, self.config, combo)
            resonances = []
            resonances.extend(conf['particle']['R_BD'])
            resonances.extend(conf['particle']['R_CD'])
            resonances.extend(conf['particle']['R_BC'])
            scan_list = deploy_scan(path, self.config['scan']['mass'], self.config['scan']['width'], self.scan_decimal, conf, self.config['scan']['resonance'], resonances, self.config['particle']['$include'])
            execute_scan(scan_list, path, self.search_step, self.converge_number)

    def draw_scan_result(self):
        print_sep('|', 50)
        print('Drawing mass and width scan results of {}...'.format(self.config['scan']['resonance']))
        time.sleep(1)
        for sample in self.config['data']['sample']:
            print_sep('-', 50)
            print('Proceeding {} sample...'.format(sample))
            time.sleep(1)
            if len(self.combos) != 1:
                print('You have to focus on one combo to perform mass and width scan, please set it!')
                exit()
            combo = self.combos[0]
            if not self.config['scan']['resonance'] in combo:
                print('The resonance you scan is not in the combo you focus on!')
                exit()
            print('Proceeding {} combo...'.format(paste(combo)))
            time.sleep(1)
            path = cur_dir + '/base_solution/' + str(sample) + '/' + paste(combo) + '/' + self.config['scan']['resonance'] + '/'
            scans = scan_seq(sample, self.config['scan']['resonance'], path, self.scan_decimal)
            scans.mass_width_nll()
