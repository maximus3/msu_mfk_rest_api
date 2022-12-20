FILENAME=result_2022-12-20_20-01-10.pdf
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "
  docker cp app_msu_mfk_rest_api:$FILENAME $FILENAME;
  docker exec app_msu_mfk_rest_api rm $FILENAME;
  exit;"
scp -P $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt):$FILENAME db/$FILENAME
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "rm $FILENAME; exit;"
echo "Done"