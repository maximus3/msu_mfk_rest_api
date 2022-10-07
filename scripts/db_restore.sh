FILENAME=$1
echo "Restoring database from $FILENAME"
scp -P $(cat deploy/port.txt) $FILENAME $(cat deploy/username.txt)@$(cat deploy/host.txt):$FILENAME
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "
  docker cp $FILENAME postgres_container:$FILENAME;
  docker exec postgres_container psql -d $(cat deploy/db_name.txt) -U $(cat deploy/db_username.txt) -f $FILENAME;
  docker exec postgres_container rm $FILENAME;
  rm $FILENAME;
  exit;"
echo "Done"