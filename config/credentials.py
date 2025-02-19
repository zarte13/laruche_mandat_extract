import configparser
from pathlib import Path

class CredentialsManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / 'config.ini'
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        
        config.read(config_path)
        return config

    def get_credentials(self):
        """Récupère les credentials du fichier config.ini"""
        try:
            return {
                'username': self.config['credentials']['username'],
                'password': self.config['credentials']['password']
            }
        except KeyError as e:
            raise KeyError(f"Missing credential in config file: {e}")

    def get_urls(self):
        """Récupère les URLs du fichier config.ini"""
        try:
            return {
                'login_url': self.config['urls']['login_url'],
                'base_url': self.config['urls']['base_url']
            }
        except KeyError as e:
            raise KeyError(f"Missing URL in config file: {e}")

    def get_settings(self):
        """Récupère les paramètres du fichier config.ini"""
        try:
            return {
                'wait_time': self.config['settings'].getint('wait_time'),
                'jobs_per_page': self.config['settings'].getint('jobs_per_page')
            }
        except KeyError as e:
            raise KeyError(f"Missing setting in config file: {e}")