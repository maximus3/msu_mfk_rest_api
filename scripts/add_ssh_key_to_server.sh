HOST=$(cat deploy/host.txt)
USERNAME=$(cat deploy/username.txt)
PORT=$(cat deploy/port.txt)

ssh-copy-id -i ~/.ssh/id_rsa.pub -p $PORT $USERNAME@$HOST