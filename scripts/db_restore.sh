exit 1
FILENAME=$1
echo "Restoring database from $FILENAME"
scp -P $(cat deploy/port.txt) db/$FILENAME $(cat deploy/username.txt)@$(cat deploy/host.txt):$FILENAME
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "
  docker cp $FILENAME postgres_msu_mfk_rest_api:$FILENAME;
  docker exec postgres_msu_mfk_rest_api psql -d $(cat deploy/db_name.txt) -U $(cat deploy/db_username.txt) -f $FILENAME;
  docker exec postgres_msu_mfk_rest_api rm $FILENAME;
  rm $FILENAME;
  exit;"
echo "Done"