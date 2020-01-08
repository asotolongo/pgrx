__author__ = 'anthony'
import logging
import logging.handlers

class log(object):
    """class general db"""

    def __init__(self,archivo):
        #logging.basicConfig(filename=archivo, level=logging.INFO,format='%(asctime)s  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p' )
        self.log = logging.getLogger('amt4')
        self.log.setLevel(logging.INFO)
        manejador = logging.handlers.RotatingFileHandler(filename=archivo, mode='a', maxBytes=10485760, backupCount=10) #10485760
        manejador.setFormatter(logging.Formatter(fmt='%(asctime)s  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p' ))
        self.log.addHandler(manejador)



    def info(self, texto):
        self.log.info(texto)