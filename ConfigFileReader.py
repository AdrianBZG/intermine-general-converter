import json

class ConfigFileReader:
    def __init__(self, configPath):
        self.configPath = configPath
        self.name = ""
        self.attributes = ""
        self.fileType = ""
        self.populateConfig(configPath)

    def populateConfig(self, path):
        with open(path) as json_file:
            data = json.load(json_file)
            self.name = data["name"]
            self.attributes = data["attributes"]
            self.fileType = data["fileType"]