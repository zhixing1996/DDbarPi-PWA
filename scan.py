import os, pickle
from pwa_generator.config_loader import ConfigLoader
from pwa_generator.config_loader.tools import string_list
conf = ConfigLoader('config.yml', converge_number = 2)
scan_list_group = conf.prepare_scan(scan_list_size = 600)

for idx, scan_list in enumerate(scan_list_group):
    if not os.path.exists(conf.scan_root_path + 'run/'): os.makedirs(conf.scan_root_path + 'run/')
    with open(conf.scan_root_path + 'run/' + 'scan_' + str(idx) + '.py', 'w') as f:
        text = """"""
        text += 'import sys\n'
        text += 'sys.path.insert(0, \'' + conf.cur_path + '\')\n'
        text += 'from pwa_generator.config_loader import ConfigLoader\n'
        text += 'conf = ConfigLoader(\'' + conf.cur_path + 'config.yml\', converge_number = 2)\n'
        text += 'scan_list = ' + str(string_list(scan_list)) + '\n'
        text += 'conf.scan(scan_list)' + '\n'
        f.write(text)
    os.system('cp ' + conf.cur_path + 'scripts/submit_scan_RES_gpu.sh ' + conf.scan_root_path + 'run/submit_scan_' + conf.config['scan']['resonance'] + '_' + str(idx) + '_gpu.sh')
    os.system('sed -i \'s/RES/' + conf.config['scan']['resonance'] + '/g\' ' + conf.scan_root_path + 'run/submit_scan_' + conf.config['scan']['resonance'] + '_' + str(idx) + '_gpu.sh')
    os.system('sed -i \'s/PATH/' + conf.scan_root_path.replace('/', '\/') + '/g\' ' + conf.scan_root_path + 'run/submit_scan_' + conf.config['scan']['resonance'] + '_' + str(idx) + '_gpu.sh')
    os.system('sed -i \'s/IDX/' + str(idx) + '/g\' ' + conf.scan_root_path + 'run/submit_scan_' + conf.config['scan']['resonance'] + '_' + str(idx) + '_gpu.sh')
    os.system('cd ' + conf.scan_root_path + 'run && sbatch submit_scan_' + conf.config['scan']['resonance'] + '_' + str(idx) + '_gpu.sh')
