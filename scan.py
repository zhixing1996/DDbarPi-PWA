from pwa_generator.config_loader import ConfigLoader
conf = ConfigLoader('config.yml', converge_number = 2)
conf.scan()
