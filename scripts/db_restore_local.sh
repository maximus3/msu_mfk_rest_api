FILENAME=$1
echo "Restoring local database from $FILENAME"
docker cp db/$FILENAME postgres_container:$FILENAME
docker exec postgres_container psql -d $(cat deploy/db_name.txt) -U $(cat deploy/db_username.txt) -f $FILENAME
docker exec postgres_container rm $FILENAME
echo "Done"