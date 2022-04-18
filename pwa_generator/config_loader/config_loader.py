from .base_config import BaseConfig
from .tools import combination_generator, combination_filter, conf_generator, paste
import os, yaml

class ConfigLoader(BaseConfig):
    """ class for loading config.conf """

    def __init__(self, file_name, share_dict = None):
        if share_dict is None:
            share_dict = {}
        super().__init__(file_name, share_dict)
        self.combos = self.generate_combination()

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
        for sample in self.config['data']['sample']:
            for combo in self.combos:
                path = './base_solution/' + str(sample) + '/' + paste(combo) + '/'
                if not os.path.exists(path): os.makedirs(path)
                with open(path + 'config.yml', 'w') as f:
                    yaml.dump(conf_generator(sample, self.config, combo), f)
