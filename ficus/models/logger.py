import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ficus_app.log',  # Set the log file name
    filemode='w'
)
logging.getLogger('httpx').setLevel(logging.ERROR)

ficus_logger = logging.getLogger('ficus_logger')
