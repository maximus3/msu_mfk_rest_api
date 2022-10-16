echo "Updating code on server from github"
ssh -p $(cat deploy/port.txt) $(cat deploy/username.txt)@$(cat deploy/host.txt) "
  cd msu_mfk_rest_api;
  git pull && make update;
  exit;"
echo "Done"