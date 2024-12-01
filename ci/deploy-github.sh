#!/bin/bash
echo "Environment: $CI_ENVIRONMENT_NAME"

mkdir -p ~/.ssh
echo "$SSH_KEY" | tr -d '\r' > ~/.ssh/deploy_key
sudo chmod 600 ~/.ssh/deploy_key
ssh -i ~/.ssh/deploy_key -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "echo Ping && exit"
ssh -i ~/.ssh/deploy_key -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "
  [ -e $CODE_FOLDER ] || git clone git@github.com:$GITHUB_REPO.git $CODE_FOLDER; exit"
ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no -p $SSH_PORT $SSH_USERNAME@$SSH_HOST "
  cd $CODE_FOLDER;
  git pull;
  echo \"$ENV\" > .env;
  make docker-stop postgres || echo \"Postgres not run\";
  make update;
  exit"