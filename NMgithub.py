#!/usr/bin/env python3
import os
from git import Repo

GITHUB_URL = "git@github.com:AndyZ666/NM_Lab.git"
LOCAL_REPO_PATH = os.path.expanduser("~/Documents/5180/midterm")
GIT_EMAIL = "13680266363zzz@gmail.com"
GIT_USERNAME = "AndyZ666"

def get_or_create_repo():
    if os.path.exists(LOCAL_REPO_PATH):
        print(f"Git repo found at {LOCAL_REPO_PATH}")
        return Repo(LOCAL_REPO_PATH)
    else:
        print(f"Cloning GitHub repo to {LOCAL_REPO_PATH}")
        return Repo.clone_from(GITHUB_URL, LOCAL_REPO_PATH)

def configure_git(repo):
    with repo.config_writer() as config:
        config.set_value("user", "email", GIT_EMAIL)
        config.set_value("user", "name", GIT_USERNAME)
    print("Git config updated.")

def add_and_commit_files(repo):
    
    repo_path = repo.working_dir
    txt_files = [f for f in os.listdir(repo_path) if f.endswith(".txt")]
    jpg_files = [f for f in os.listdir(repo_path) if f.endswith(".jpg")]

    if not txt_files and not jpg_files:
        print("No .txt or .jpg files found. Skipping push.")
        return False

    staged_files = set(repo.git.ls_files().split("\n"))  
    new_files = [f for f in txt_files + jpg_files if f not in staged_files]

    if not new_files:
        print("No new .txt or .jpg files to add.")
        return False

    for file in new_files:
        file_path = os.path.join(repo_path, file)
        print(f"Adding {file_path} to Git...")
        repo.git.add(file_path)

    if repo.is_dirty():
        repo.index.commit("Upload new .txt and .jpg files")
        print("Files committed successfully.")
        return True
    else:
        print("No changes to commit.")
        return False

def push_modified_files(repo):
    changed_files = [item.a_path for item in repo.index.diff(None)]
    if changed_files:
        print(f"Pushing modified files: {', '.join(changed_files)}")
        repo.git.add(update=True)
        repo.index.commit("Update modified files")
        repo.remote().push()
        print("Push successful.")
    else:
        print("No modified files to push.")

if __name__ == "__main__":
    repo = get_or_create_repo()
    configure_git(repo)

    if add_and_commit_files(repo):
        repo.remote().push()
        print("Initial .txt and .jpg files pushed.")

    push_modified_files(repo)