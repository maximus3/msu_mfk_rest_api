FILENAME=scheduler_logs_$(date +%Y%m%d_%H%M%S).log
echo "Get scheduler logs to $FILENAME"
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "
  docker logs scheduler >& /tmp/$FILENAME;
  exit;"
scp -P $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt):/tmp/$FILENAME logs/$FILENAME
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "rm /tmp/$FILENAME; exit;"
echo "Done"