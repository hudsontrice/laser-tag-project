# Photon Laser Tag Project (Sprint 1)

Language: Python 3

Current files:
```
README.md         # Project documentation and instructions
requirements.txt  # List of Python dependencies for the project
.gitignore        # Specifies files Git should ignore
.gitattributes    # Configures how Git handles line endings and file types
```

requirements.txt: list Python packages (install with `pip install -r requirements.txt`).

Sprint 1 to-do:
- [x] Choose language
- [x] Create repo
- [ ] Slack channel + roster
- [ ] Trello board
- [ ] Weekly status posts (Thu)
- [ ] Word doc (team, members, language, issues) submitted

## How to Get (Clone) This Repo to Your PC
1. Pick (or create) a folder where you keep projects.
2. Open a terminal in that folder (Right click -> Open in Terminal or use `cd`).
3. Run:
```
git clone https://github.com/xXTomatoXx/laserTagProject.git
```
4. Go into it:
```
cd laserTagProject
```
5. (Optional) Check you are on main:
```
git branch
```
6. Make a tiny change, then save & push (example first commit after clone):
```
git add README.md
git commit -m "Test commit"
git push
```
If you get an auth error, make sure GitHub login / token is set up (We can do this in class it may be bc I added ur name wrong)

Basic terminal commands:
```
git status          # What changed?
git add .           # Tell Git to track today's changes
git commit -m "msg" # Save a snapshot with a message
git push            # Upload your snapshots
git pull            # Get teammates' latest snapshots
```

If you only changed one file you can do: `git add that_file_name`

### What is .gitignore?
    It tells Git which files to skip (caches, virtual envs, secrets, logs, databases).

### Typical Flow
1. git pull when you first open codebase
2. Make changes
3. git add . (the . will add all ur unadded files)
4. git commit -m "Describe change"
5. git push