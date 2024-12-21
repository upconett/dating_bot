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
            self.client_id = denv["client_id"]
            self.client_secret = denv["client_secret"]
            self.payment_token = denv["payment_token"]
            self.redirect_url = denv["redirect_url"]
        except KeyError as key:
            raise DotEnvException(f"Key {key} required in {dotenv_path} file!")

        if os.path.exists("admins.txt"):
            with open("admins.txt", 'r') as file:
                self.admins = [int(id) for id in file.readlines()]
