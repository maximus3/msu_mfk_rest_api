#!/bin/bash
echo "Environment: $CI_ENVIRONMENT_NAME"

echo "GITHUB_URL=$(git remote get-url origin)" >> $GITHUB_ENV
echo "GITHUB_REPO=${{ github.repository }}" >> $GITHUB_ENV

mkdir -p ~/.ssh
echo "${{ secrets.SSH_KEY }}" | tr -d '\r' > ~/.ssh/deploy_key
sudo chmod 600 ~/.ssh/deploy_key
ssh -i ~/.ssh/deploy_key -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "echo "Ping" && exit"
ssh -i ~/.ssh/deploy_key -p ${{ secrets.SSH_PORT }} -o StrictHostKeyChecking=no ${{ secrets.SSH_USERNAME }}@${{ secrets.SSH_ADDRESS }} "
  echo "Ping" && exit"
ssh -i ~/.ssh/deploy_key -p ${{ secrets.SSH_PORT }} -o StrictHostKeyChecking=no ${{ secrets.SSH_USERNAME }}@${{ secrets.SSH_ADDRESS }} "
  [ -e ${{ github.event.repository.name }} ] || git clone git@github.com:$GITHUB_REPO.git; exit"
ssh  -i ~/.ssh/deploy_key -p ${{ secrets.SSH_PORT }} -o StrictHostKeyChecking=no ${{ secrets.SSH_USERNAME }}@${{ secrets.SSH_ADDRESS }} "
  cd ~/${{ github.event.repository.name }};
  git pull;
  echo \"${{ secrets.ENV }}\" > .env;
  make docker-stop postgres || echo \"Postgres not run\";
  make update;
  exit"