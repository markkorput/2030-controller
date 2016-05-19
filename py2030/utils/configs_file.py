class ConfigsFile:
    def __init__(self, options = {}):
        # configure
        self.options = {}
        self.configure(options)

        # internal representation of the configs
        self.configs_data = {}

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    def load(self):
        import xml.etree.ElementTree as ET
        tree = ET.parse(self.options['path'])
        del ET

        # get all configs elements
        configels = tree.getroot().find(self.options['configs_root_el').findall('config_el')
        # reset
        self.configs_data = {}

        # loop over each config element
        for cfgel in configels:
            # loop over each param node in this config el
            for param in list(cfgel):
                # set the param value for this config
                self.update_param(param.attrib['name'], param.name, param.text)

        if 'verbose' in self.options and self.options['verbose']:
            print '[ConfigsFiles.load] result:', self.configs_data

    def save(self):
        print 'TODO: ConfigsFile.save with: ', self.configs_data

    def update_param(self, config_name, param_name, param_value):
        if not config_name in self.configs_data:
            self.configs_data[config_name] = {}
        self.configs_name[param_name] = param_value
