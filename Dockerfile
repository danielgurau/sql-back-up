FROM mysql:latest

# dependency: requires Python to be installed (no version specified)
RUN apt-get update
RUN apt-get install python -y

# actual tool
COPY db_backup.py db_backup.py

# todo: create "/backup/my.cnf" file with host and user (credentials) variables or alter the script

ENTRYPOINT ["python", "db_backup.py"]
