# How generate files to deploy?

## 1. Generate files

```bash
echo YOUR_HOSTNAME > deploy/host.txt
echo YOUR_USERNAME > deploy/username.txt
echo YOUR_PORT > deploy/port.txt
```

## 2. Generate files

```bash
make generate-deploy-key
```

## 3. Add GitHub/Gitlab Secrets

- `.env` to `ENV`
- `host.txt` to `SSH_ADDRESS`
- `port.txt` to `SSH_PORT`
- `username.txt` to `SSH_USERNAME`
- `id_rsa` to `SSH_KEY`

### How to add secrets in GitHub?

- Open `Settings` of your repo
- Open `Secrets` - `Actions`
- Click on `New repository secret`

## 4. Security

**MAKE SURE YOU DON'T COMMIT THE GENERATED FILES TO THE REPOSITORY**

CHECK `.gitignore`
