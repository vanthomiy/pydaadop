# Git Quick Commands

## Branches
```bash
# List branches
git branch

# Create new branch
git branch <branch-name>

# Switch to branch
git checkout <branch-name>

# Create and switch in one step
git checkout -b <branch-name>
````

## Commit

```bash
# Stage files
git add <file>       # single file
git add .            # all changes

# Commit changes
git commit -m "Commit message"
```

## Push

```bash
# Push current branch to remote
git push origin <branch-name>
```

## Pull Request (GitHub CLI)

```bash
# Create pull request from current branch
gh pr create --base main --head <branch-name> --title "PR title" --body "Description"

# List PRs
gh pr list

# Merge PR
gh pr merge <pr-number> --merge
```