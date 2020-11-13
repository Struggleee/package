# gunicorn.py
import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing
bind = '0.0.0.0:80'      
backlog = 512                #The maximum number of pending connections.
#chdir = '/home/test/server/bin'  #working directory
timeout = 6000      

workers = multiprocessing.cpu_count() * 2 + 1    #process number
loglevel = 'info' 
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'    
accesslog = "/home/itbd_nttdata/log/gunicorn_access.log"      
errorlog = "/home/itbd_nttdata/log/gunicorn_error.log"  

