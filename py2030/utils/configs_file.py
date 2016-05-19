class ConfigsFiles:
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
            # gather all dat afor this config
            cfgdata = {}
            for param in list(cfgel):
                cfgdata[param.attrib['name']] = param.text

            if 'verbose' in self.options and self.options['verbose']:
                print '[ConfigsFiles.load]', param.attrib['name'], cfgdata
            self.configs_data[cfgel.name] = cfgdata
