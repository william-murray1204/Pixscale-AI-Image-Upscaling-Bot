#!/usr/bin/env python3
from multiprocessing import Pool
from os import getenv, system
from logging import getLogger
from traceback import format_exc
from dotenv import load_dotenv
from datetime import datetime
from pixscale_db import DBHelper
import requests


# Retrieves sensitive data from .env file
load_dotenv()
EDWIN_API_KEY = getenv('EDWIN_API_KEY')
ADMIN_CHATID = getenv('ADMIN_CHATID')

# Create the MySQL pool
db = DBHelper()

logger = getLogger()

# Sends Telegram notifications
def notifications(message_content):
    url = f"https://api.telegram.org/bot{EDWIN_API_KEY}"
    params = {"chat_id": ADMIN_CHATID, "text": message_content}
    r = requests.get(url + "/sendMessage", params=params)

try:
    db.setup()  # Creates the necessary pixscale tables if they do not already exist
    all_processes = (
        'ai_queue_handler.py',
        'pixscale.py')

    def execute(process):
        system(f'python {process}')

    if __name__ == '__main__':
        process_pool = Pool(processes=2)
        process_pool.map(execute, all_processes)
except Exception as Argument:
    logger.warning(format_exc())
    notifications(
        f"[SERVER ENCOUNTERED] Pixscale Error: \n{format_exc()}") 
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    db.log_error(dt_string, "run.py", format_exc(), None)
    


