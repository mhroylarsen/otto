from ctypes import util
import tomlkit
from pkgutil import walk_packages
from importlib import import_module

from otto import utils

class Config:    
    def generate(self):
        """Generates a config in the user's home directory from the utility modules"""
        utilconfigs = self.getpackageconfigurations()
        configdoc = tomlkit.document()
        for tableheader, tablevalue in utilconfigs.items():
            table = tomlkit.table()
            for value in tablevalue:
                table.add(value, utilconfigs[tableheader][value])
            configdoc.add(tableheader, table)
        return tomlkit.dumps(configdoc)

    def getpackageconfigurations(self):
        """Retrieves the config packages from the utility modules"""
        import otto.utils
        packages = {}
        for sub in walk_packages(otto.utils.__path__, otto.utils.__name__ + "."):
            if sub.name.endswith(".config"):
                utilconfig = getattr(import_module(sub.name), "Config")
                if hasattr(utilconfig, "CONFIGURATION"):
                    packages.update(utilconfig.CONFIGURATION)
        
        return packages

    def getvaluefromconfig(self, configctx, valuelookup):
        """Takes the config value lookuo, and looks it up against the config context"""
        parsedctx = tomlkit.parse(configctx)

        return parsedctx[valuelookup[0]][valuelookup[1]]
    
    def update(self, configctx):
        """Takes in the config context, compares it to the configs in the util packages """
        utilconfigs = self.getpackageconfigurations()
        otconfig = tomlkit.parse(configctx)

        # update existing config for removed sections/modules
        for section in list(otconfig.keys()):
            if section not in list(utilconfigs.keys()):
                del otconfig[section]
        
        # update existing config for new sections/attributes
        for section in list(utilconfigs.keys()):
            if section not in list(otconfig.keys()):
                otconfig[section] = utilconfigs[section]
            else:
                for attribute in list(utilconfigs[section].keys()):
                    if attribute not in list(otconfig[section].keys()):
                        otconfig[section][attribute] = utilconfigs[section][attribute]
        return tomlkit.dumps(otconfig)
