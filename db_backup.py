#!/usr/bin/python
############################################################
#
# This script is used to back-up a mysql database
#
# Script takes the name of the database as input
# Script also takes the type of back-up as imput 
# Options are: 
#   -d DAILY
#   -w WEEKLY
#   -m MONTLY
#   -y YEARLY
#
############################################################

import time
import datetime
import sys, os
import argparse
import logging
import ConfigParser
from logging import handlers, Formatter

if not os.geteuid()==0:
    sys.exit("\nOnly root can run this script\n")

#Parse the input
parser = argparse.ArgumentParser(description="This script can be used to back-up a mysql database")
parser.add_argument("db_name" , help="Database name" )
parser.add_argument("--option", choices=['d','w','m','y'], help="Daily, Weekly, Montly, Yearly")
args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read(os.path.expanduser('/backup/my.cnf'))
#Define the variables
DB_HOST = config.get('client', 'host')
DB_USER = config.get('client', 'user')
DB_NAME = args.db_name
BACKUP_TYPE = args.option
DATEETIME = time.strftime('%d-%m-%Y-%H:%M')
LOG_FILENAME = '/backup/log/backup.out'

#Create Logger
logger = logging.getLogger()
log_format = Formatter("%(asctime)s %(levelname)s : %(message)s")
handler = handlers.RotatingFileHandler(LOG_FILENAME,maxBytes=10000000,backupCount=2)
handler.setFormatter(log_format)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

#Select back-up folder depending on the option selected.
if BACKUP_TYPE == 'd':
	BACKUP_PATH = '/backup/'+ DB_NAME + '/daily'
	logging.info('Staring DAILY backup')
elif  BACKUP_TYPE == 'w':
	logging.info('Staring WEEKLY backup')
	BACKUP_PATH = '/backup/'+ DB_NAME + '/weekly'
elif BACKUP_TYPE == 'm':
	logging.info('Staring MONTHLY backup')
	BACKUP_PATH = '/backup/'+ DB_NAME + '/montly'
elif BACKUP_TYPE == 'y':
	logging.info('Staring YEARLY backup')
	BACKUP_PATH = '/backup/'+ DB_NAME + '/yearly'
else:
	logging.info('Staring backup')
	BACKUP_PATH = '/backup/'+ DB_NAME
	
#Check if the folder exists. If not create it

if not os.path.exists(BACKUP_PATH):
	os.makedirs(BACKUP_PATH)

dumpcmd = "mysqldump --defaults-extra-file=/backup/my.cnf -u " + DB_USER + " " + DB_NAME + " > " + BACKUP_PATH + "/" + DB_NAME + "-" + DATEETIME + "-" + str(BACKUP_TYPE) + ".sql"

if os.system(dumpcmd) == 0:
	logging.info("Your backups for DB: " + DB_NAME + "has been created in '" + BACKUP_PATH + "' directory")
	logging.info('Backup script completed')
else:
	logging.error('Backup script failed!')

print "Your backup file is now available here: " + BACKUP_PATH + "/" + DB_NAME + "-" + DATEETIME + "-" + str(BACKUP_TYPE) + ".sql"