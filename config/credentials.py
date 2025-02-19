# main.py
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

username = config['credentials']['username']
password = config['credentials']['password']