import configparser

class ConfigService:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('data/config.ini')

    def get_value(self, section, option):
        value = self.config.get(section, option, fallback="dark")
        return value

    def set_value(self, section, option, value):
        try:
            self.config.set(section, option, value)
            with open('data/config.ini', 'w') as configfile:
                self.config.write(configfile)
        except configparser.NoSectionError:
            self.config.add_section(section)
            self.config.set(section, option, value)
            with open('data/config.ini', 'w') as configfile:
                self.config.write(configfile)
