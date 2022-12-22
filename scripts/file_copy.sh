FILENAME=$1
echo "Downloading file $FILENAME"
scp -P $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt):msu_mfk_rest_api/db/$FILENAME db/$FILENAME
echo "Done"