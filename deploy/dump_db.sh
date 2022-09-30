FILENAME=backup_$(date +%Y%m%d_%H%M%S).sql
echo "Dumping database to $FILENAME"
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "
  docker exec postgres_container pg_dump -f $FILENAME -d $(cat deploy/db_name.txt) -U $(cat deploy/db_username.txt)
  docker cp postgres_container:data_dump.sql $FILENAME;
  docker exec postgres_container rm $FILENAME;
  exit;"
scp -P $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt):$FILENAME db/$FILENAME
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "rm $FILENAME; exit;"