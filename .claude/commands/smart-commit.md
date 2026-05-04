# Comando: Smart Commit

Your goal is to commit all changes since the last commit, keeping documentation and GitHub Issues in sync.

## Steps

### 1. Analyze changed files
- Run `git diff --name-only HEAD` and `git status` to list all modified, added, and deleted files
- For each changed file, understand what was modified and why
- Elaborate a clear summary of all changes grouped by context (e.g., "Authentication", "Destinations API", "Instagram Extractor")
- Print the summary to the user

### 2. Update documentation if needed
- Read all files inside the `docs/` folder
- Cross-check the change summary against the existing documentation
- If any doc is outdated or missing coverage for the changes made, update it accordingly
- If a new feature was added and there is no documentation for it, create a new doc file inside `docs/`
- Print to the user which docs were updated or created, and why

### 3. Update the roadmap
- Read `docs/roadmap.md`
- Check if any item listed in the roadmap has been fully implemented based on the change summary
- If yes, mark it as completed using the `[x]` checkbox format
- Print to the user which roadmap items were marked as completed

### 4. Sync completed roadmap items with GitHub Issues
- Run `gh issue list --state open --label roadmap` to get all open roadmap issues
- For each roadmap item marked as completed in step 3, find the matching GitHub Issue by title
- If a match is found, close the issue with a comment:
  ```
  gh issue close <number> --comment "✅ Completed in this commit. See roadmap.md for details."
  ```
- Print to the user which issues were closed

### 5. Stage and commit
- Run `git add .` to stage all changes (including any doc updates from steps 2 and 3)
- Build the commit message using this format:
  ```
  <type>(<scope>): <short summary>

  Changes:
  - <change 1>
  - <change 2>
  - ...

  Docs updated: <list or "none">
  Roadmap items completed: <list or "none">
  Issues closed: <list or "none">
  ```
  Where `type` is one of: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`
- Run `git commit -m "<message>"`
- Print the final commit message to the user

## Rules
- Never commit `.env` files or secrets
- Never modify `roadmap.md` to remove items — only mark them as `[x]`
- If there is nothing to commit, inform the user and stop
- Always print every step as it happens so the user can follow along
