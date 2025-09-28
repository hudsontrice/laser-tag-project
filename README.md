# Photon Laser Tag Project (Sprint 1)

Language: Python 3

Current files:
```
README.md         # Project documentation and instructions
requirements.txt  # List of Python dependencies for the project
.gitignore        # Specifies files Git should ignore
.gitattributes    # Configures how Git handles line endings and file types
```
## Team Members

| GitHub Username | Real Name       |
| --------------- | --------------- |
| [`@hudsontrice`](https://github.com/hudsontrice)    | *Hudson Trice* |
| [`@joshagodoy`](https://github.com/joshagodoy)      | *Josh Godoy* |
| [`@houstonmyer`](https://github.com/houstonmyer)      | *Houston Myer* |
| [`@jacksonharmon2`](https://github.com/jacksonharmon2)      | *Jackson Harmon* |
| [`@griffinkminick`](https://github.com/griffinkminick)      | *Griffin Minick* |

requirements.txt: list Python packages (install with `pip install -r requirements.txt`).

## How to Get (Clone) This Repo to personal PC
1. Pick (or create) a folder where you keep projects.
2. Open a terminal in that folder (Right click -> Open in Terminal or use `cd`).
3. Run:
```
git clone https://github.com/xXTomatoXx/laserTagProject.git
```

### Basic Git Commands
```
git status          # Shows which files have been changed
git add .           # '.' Stages all changed files for commit, or you can just use file names if you only changed a couple
git commit -m "msg" # Creates a commit with your changes and a message
git push            # Uploads your commits to the remote repository
git pull            # Downloads the latest changes from the remote repository
git checkout -b     # Creates and switches to a new branch
```


### What is .gitignore?
A configuration file that tells Git which files to ignore when tracking changes. This typically includes temporary files, build artifacts, virtual environments, credentials, logs, and database files that shouldn't be in version control.

### Git Workflow with Branches

1. Update your local main first:
    ```
    git checkout main
    git pull
    ```

2. Create and switch to a new branch for your feature:
    ```
    git checkout -b feature/short-name
    ```

3. Make your code changes

4. Stage and commit changes:
    ```
    git add .
    git commit -m "Describe changes"
    ```

5. Push your branch to the remote repository:
    ```
    git push -u origin feature/short-name  # First push sets upstream
    ```

6. On GitHub website: open a Pull Request from your branch into main
