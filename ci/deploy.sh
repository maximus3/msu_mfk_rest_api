#!/bin/bash
echo "Environment: $CI_ENVIRONMENT_NAME"
apt-get update && apt-get install openssh-client -y
mkdir -p ~/.ssh
cat $SSH_KEY_FILE | tr -d '\r' > ~/.ssh/deploy_key
chmod 600 ~/.ssh/deploy_key
ssh -i ~/.ssh/deploy_key -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "echo "Ping" && exit"
ssh -i ~/.ssh/deploy_key -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "
  [ -e $CODE_FOLDER ] || (git clone git@$CI_SERVER_HOST:$CI_PROJECT_NAMESPACE/$REPO_NAME.git $CODE_FOLDER &&
  cd $CODE_FOLDER) && exit"
ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no -p $SSH_PORT $SSH_USERNAME@$SSH_HOST "
  cd $CODE_FOLDER;
  git checkout $REPO_BRANCH;
  git pull;
  echo \"$ENV\" > .env;
  make docker-stop postgres || echo \"Postgres not run\";
  make update;
  exit"