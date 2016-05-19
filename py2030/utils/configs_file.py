import xml.etree.ElementTree as ET

class ConfigsFile:
    def __init__(self, options = {}):
        # configure
        self.options = {}
        self.configure(options)

        self.root_el_tag = None

        # internal representation of the configs
        self.configs_data = {}

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    def load(self):
        print 'ConfigsFile loading', self.options['path']
        tree = ET.parse(self.options['path'])

        # get all configs elements
        self.root_el_tag = tree.getroot().tag
        configels = tree.getroot().find(self.options['configs_root_el']).findall(self.options['config_el'])
        # reset
        self.configs_data = {}

        # loop over each config element
        for cfgel in configels:
            if not 'name' in cfgel.attrib:
                continue
            # loop over each param node in this config el
            for param in list(cfgel):
                # set the param value for this config
                self.update_param(cfgel.attrib['name'], param.tag, param.text)

        if 'verbose' in self.options and self.options['verbose']:
            print '[ConfigsFiles.load] result:', self.configs_data

    def save(self):
        print 'ConfigsFile saving to', self.options['path']
        if 'verbose' in self.options and self.options['verbose']:
            print ' - data: ', self.configs_data

        root = ET.Element(self.root_el_tag)
        configroot = ET.SubElement(root, self.options['configs_root_el'])
        confignames = self.configs_data.keys()
        confignames.sort()
        for name in confignames:
            configel = ET.SubElement(configroot, self.options['config_el'])
            configel.set('name', name)
            paramnames = self.configs_data[name].keys()
            paramnames.sort()
            for param_name in paramnames:
                paramel = ET.SubElement(configel, param_name)
                paramel.text = str(self.configs_data[name][param_name])

        # file = open(self.options['path'], 'w')
        ET.ElementTree(root).write(self.options['path'])

    def update_param(self, config_name, param_name, param_value):
        if not config_name in self.configs_data:
            self.configs_data[config_name] = {}
        self.configs_data[config_name][param_name] = param_value
