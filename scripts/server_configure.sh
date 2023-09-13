sudo apt update

# make
sudo apt install make -y

# docker
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y
sudo apt update
if apt-cache policy docker-ce | grep "https://download.docker.com/linux/ubuntu"
then
  echo "OK";
else
  echo "ERROR in docker installation";
  exit 1;
fi
sudo apt install docker-ce -y
sudo usermod -aG docker ${USER}
# need exit from server here
docker --version

# docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
