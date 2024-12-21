# TODO : move to another package, should not be in telegram

import os
from dotenv import dotenv_values

class DotEnvException(Exception): pass

class Config:
    def __init__(self, dotenv_path: str = ".env"):
        if not os.path.exists(dotenv_path):
            raise DotEnvException(f"No {dotenv_path} file!")

        denv = dotenv_values(dotenv_path)
        
        try:
            self.token = denv["token"]
            self.admins = denv["admins"]
            self.client_id = denv["client_id"]
            self.client_secret = denv["client_secret"]
        except KeyError as key:
            raise DotEnvException(f"Key {key} required in {dotenv_path} file!")