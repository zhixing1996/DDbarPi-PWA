from .base_config import BaseConfig
from .tools import combination_generator, combination_filter, conf_generator, paste, print_sep
import os, yaml, time
cur_dir = os.path.abspath(os.path.dirname('__file__'))

class ConfigLoader(BaseConfig):
    """ class for loading config.conf """

    def __init__(self, file_name, share_dict = None):
        if share_dict is None:
            share_dict = {}
        super().__init__(file_name, share_dict)
        self.combos = self.generate_combination()

    def generate_combination(self):
        print_sep('|', 50)
        print('Generating combinations...')
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
