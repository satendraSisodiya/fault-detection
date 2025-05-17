import logging
import os
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime("%m_%d_%Y_%H_%M_%s")}.log"

LOG_PATH = os.path.join(os.getcwd(),"logs",LOG_FILE)

os.makedirs(LOG_PATH, exist_ok = True)

LOG_FILE_PATH = os.path.join(LOG_PATH,LOG_FILE)

logging.basicConfig(
    name = LOG_FILE_PATH,
    level = logging.INFO,
    formate = "[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s"
)