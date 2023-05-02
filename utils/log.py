from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler

def start_log(company_name, store_name):
    #Will uncomment the following to when running in UNIX or LINUX, just for windows we are using log file in same directory
    #Path("/home/opc/doorcounts-ai/doorcounts-ai-test/logs").mkdir(exist_ok=True)
    #logging.basicConfig(filename='/var/log/doorcounts/ai-app.log',
    logging.basicConfig(
        handlers=[TimedRotatingFileHandler('log/ai-app-{}-{}.log'.format(company_name, store_name), when='midnight', backupCount=5)],
        #filename='ai-app-{}-{}.log'.format(company_name, store_name),
        #filemode='a',
        format='%(levelname)s %(asctime)s %(funcName)s %(lineno)d - %(message)s',
        level='DEBUG'
    )
