import argparse
from ConfigFileReader import ConfigFileReader

def parse_args():
    parser = argparse.ArgumentParser(description = "", epilog = "")
    parser.add_argument("-cf", "--configFile", help="Path to the config file to be read in for further transformation into a converter (REQUIRED).", dest="configFile")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()     
    configFileReader = ConfigFileReader(args.configFile)