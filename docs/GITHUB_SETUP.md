# GitHub Repo Setup and Push Steps

This project is ready to be pushed to GitHub, but the connector available in this environment cannot create a brand-new repository directly. It can work with existing repositories.

## Recommended repository name

```text
personal-medical-assistant-vapi
```

## Option A. Create the repo in GitHub UI

1. Sign in to GitHub.
2. Click **New repository**.
3. Repository owner: `prateek-wahane`
4. Repository name: `personal-medical-assistant-vapi`
5. Choose **Public** or **Private**.
6. Do not add a README or `.gitignore` because this project already includes them.
7. Click **Create repository**.

Then push from your terminal:

```bash
git init
git add .
git commit -m "Initial commit: Personal Medical Assistant with Vapi"
git branch -M main
git remote add origin https://github.com/prateek-wahane/personal-medical-assistant-vapi.git
git push -u origin main
```

## Option B. Use GitHub CLI

If you have `gh` installed and authenticated:

```bash
gh repo create prateek-wahane/personal-medical-assistant-vapi --public --source=. --remote=origin --push
```

For a private repo:

```bash
gh repo create prateek-wahane/personal-medical-assistant-vapi --private --source=. --remote=origin --push
```

## Included helper scripts

### macOS / Linux

```bash
bash scripts/create_github_repo.sh public
```

### Windows PowerShell

```powershell
./scripts/create_github_repo.ps1 -Visibility public
```

Change `public` to `private` if you want a private repository.

## After push

Recommended next steps:
- add repository topics such as `vapi`, `fastapi`, `medical-assistant`, `voice-ai`, `google-calendar`
- add secrets for deployment if you set up CI or hosting
- protect the main branch if this becomes a team project
