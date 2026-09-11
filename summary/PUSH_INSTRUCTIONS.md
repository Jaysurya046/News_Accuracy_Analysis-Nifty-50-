# 🚀 GitHub Push & Repository Management Guide

This repository is fully configured, version-controlled with 15 semantic commits, and connected to its remote GitHub repository:
**`https://github.com/Jaysurya046/News_Accuracy_Analysis-Nifty-50-.git`**

---

## 📋 Current Repository Status

- **Remote URL**: `https://github.com/Jaysurya046/News_Accuracy_Analysis-Nifty-50-.git`
- **Active Branch**: `main` (tracking `origin/main`)
- **Git User**: `Jaysurya046` (`jaysurya046@gmail.com`)
- **Local Path**: `c:\Users\jayas\OneDrive\Desktop\web_development\Quant-Trading`

---

## 🔄 Daily Git Workflow

### 1. Check Working Tree Status
Before staging or committing, check for modified or untracked files:
```powershell
git status
```

### 2. Stage Changes
Stage specific modified files or all changes:
```powershell
# Stage specific files (recommended)
git add summary/
git add src/

# Or stage all changes
git add .
```

### 3. Create a Semantic Commit
Write clear, descriptive commit messages describing the changes made:
```powershell
git commit -m "Update docs to reflect current modular repository architecture"
```

### 4. Push to GitHub
Push your local commits directly to the remote `main` branch:
```powershell
git push origin main
```

---

## 🔑 Authentication Guide

If Git prompts for credentials when pushing, use one of the following methods:

### Option A: GitHub Personal Access Token (Recommended)
1. Navigate to **GitHub** → **Settings** → **Developer Settings** → **Personal Access Tokens** → **Tokens (classic)** (or Fine-grained tokens).
2. Generate a token with the `repo` scope enabled.
3. When prompted in the terminal:
   - **Username**: `Jaysurya046`
   - **Password**: *Paste your Personal Access Token*
4. Optionally cache your credentials with Git Credential Manager:
   ```powershell
   git config --global credential.helper manager
   ```

### Option B: SSH Authentication
1. Generate an SSH key (if not already created):
   ```powershell
   ssh-keygen -t ed25519 -C "jaysurya046@gmail.com"
   ```
2. Add the public key (`~/.ssh/id_ed25519.pub`) to your GitHub account under **Settings** → **SSH and GPG keys**.
3. Switch your Git remote to SSH:
   ```powershell
   git remote set-url origin git@github.com:Jaysurya046/News_Accuracy_Analysis-Nifty-50-.git
   ```
4. Push using SSH:
   ```powershell
   git push origin main
   ```

---

## 🛠️ Useful Git Commands

| Purpose | Command |
|:--------|:--------|
| View remote URLs | `git remote -v` |
| View recent commit history | `git log --oneline -n 10` |
| View detailed commit diff | `git show <commit-hash>` |
| Pull latest remote changes | `git pull --rebase origin main` |
| Discard uncommitted file changes | `git restore <filename>` |
| View changes before staging | `git diff` |
| View staged changes | `git diff --staged` |

---

## 📁 GitHub Repository Contents

When viewing the repository on GitHub (`https://github.com/Jaysurya046/News_Accuracy_Analysis-Nifty-50-`), the structure consists of:

```
News_Accuracy_Analysis-Nifty-50-/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── config.py
├── run_pipeline.py
├── data/
│   ├── raw/
│   ├── sources_1year/
│   ├── sources_3year/
│   └── processed/
├── summary/
│   ├── DEPLOYMENT_SUMMARY.txt
│   ├── PROJECT_SUMMARY.md
│   └── PUSH_INSTRUCTIONS.md
├── models/
│   ├── models_lgb_folds.joblib
│   └── training_metrics.json
├── reports/
│   ├── figures/
│   ├── text/
│   └── comparison_reports/
└── src/
    ├── config.py
    ├── scrapers/
    ├── data_generators/
    ├── analysis/
    ├── models/
    ├── visualization/
    └── utils/
```

---

**Repository is synchronized and ready!**
