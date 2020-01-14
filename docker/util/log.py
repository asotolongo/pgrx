__author__ = 'anthony'
import logging
import logging.handlers

class log(object):
    """class general db"""

    def __init__(self,p_file):
        #logging.basicConfig(filename=archivo, level=logging.INFO,format='%(asctime)s  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p' )
        self.log = logging.getLogger('pgrx')
        self.log.setLevel(logging.INFO)
        l_manager = logging.handlers.RotatingFileHandler(filename=p_file, mode='a', maxBytes=10485760, backupCount=10) #10485760
        l_manager.setFormatter(logging.Formatter(fmt='%(asctime)s  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p' ))
        self.log.addHandler(l_manager)



    def info(self, p_text):
        self.log.info(p_text)