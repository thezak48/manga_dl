import configparser
import os


class ConfigHandler:
    def __init__(self, logger, path):
        self.config = configparser.ConfigParser()
        self.logger = logger
        self.path = path

        # If config file doesn't exist, create one with default values.
        if not os.path.exists(path):
            self.logger.error("No config file found. Generating one.")
            self._generate_default_config()

        # Read existing config file.
        self.config.read(path)

    def get(self, section, option):
        return self.config.get(section, option)

    def getint(self, section, option):
        return self.config.getint(section, option)

    def getboolean(self, section, option):
        return self.config.getboolean(section, option)

    def _generate_default_config(self):
        self.config["General"] = {
            "mangas": "./data/manga.txt",
            "multi_threaded": "True",
            "num_threads": "10",
            "save_location": "./data/manga",
        }

        with open(self.path, "w") as configfile:
            self.config.write(configfile)
