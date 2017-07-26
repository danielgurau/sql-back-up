#!/usr/bin/env bash
echo "This test will take less than a minute (there is a timeout of 10 seconds)"
echo ""

# generate IDs
HASH=$(uuidgen)
echo "Passphrase: ${HASH}"
CONTAINER_ID=$(docker run -d --name mysql-test-backup-$HASH -e MYSQL_ROOT_PASSWORD=$HASH mysql:latest)
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID)

echo "Container ID: ${CONTAINER_ID}"
MARKER="MARKER-${CONTAINER_ID}-${HASH}"
echo ""

# insert data
sleep 10
set -x #echo on
docker exec -it $CONTAINER_ID mysql -uroot -p$HASH -e "create database sample_test; use sample_test; CREATE TABLE road (name VARCHAR(500), created_at DATE); insert into road (name, created_at) values (\"${MARKER}\", \"2017-05-01 00:00:00\")"
set +x #echo off
RAW_DUMP=$(docker exec -it $CONTAINER_ID mysqldump -uroot -p$HASH --databases sample_test | tail -n +2 -f -)
echo ""

# test: initial setup (create a DB, table and insert a row)
if [[ $RAW_DUMP = *"$MARKER"* ]]; then
    echo "Initial setup successful"
else
    echo "Initial setup failed"
fi
echo ""

# keep for debug
SETUP_DUMP_FILE="dump-initial.sql"
APP_DUMP_FILE="dump-app.sql"

echo "Raw MySQL initial dumped to ${SETUP_DUMP_FILE}"
echo ""
echo $RAW_DUMP > $SETUP_DUMP_FILE
# cat $SETUP_DUMP_FILE
# rm $SETUP_DUMP_FILE
echo ""

# build the container (requirements: mysqldump, python, /backup/my.cnf setup)
docker build -t db_backup .

# show usage
docker run --name db_backup_instance --rm db_backup -h

# run backup
docker run --name db_backup_instance --rm db_backup sample_test > $APP_DUMP_FILE
# todo send credentials and host via arguments
# example:
#   docker run \
#      --name db_backup_instance \
#      --rm db_backup $HASH:root@$CONTAINER_IP:3306/sample_test $APP_DUMP_FILE

# cleanup
docker rm -f $CONTAINER_ID
