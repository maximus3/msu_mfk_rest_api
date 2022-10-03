HOST=$(cat host.txt)
USERNAME=$(cat username.txt)
PORT=$(cat port.txt)

ssh-keygen -t rsa -b 4096 -C "$USERNAME@$HOST" -q -N "" -f id_rsa
ssh-copy-id -i id_rsa.pub -p $PORT $USERNAME@$HOST
ssh -p $PORT $USERNAME@$HOST "ssh-keyscan $HOST > known_hosts_to_git_ci.txt;exit"
scp -i ~/.ssh/id_rsa -P $PORT $USERNAME@$HOST:~/known_hosts_to_git_ci.txt known_hosts_to_git_ci.txt
ssh -p $PORT $USERNAME@$HOST "rm known_hosts_to_git_ci.txt;exit"