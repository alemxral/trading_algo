import subprocess
from datetime import datetime
import os

def commit_and_push(files_to_commit=None, repo_path="."):
    """
    Stage, commit, and push changes using Git CLI via subprocess.

    Args:
        files_to_commit (list): List of file paths to commit. If None, commits the entire directory.
        repo_path (str): Path to the local Git repository (default: current directory).
    """
    try:
        print("\n🔄 Starting Git operations...")

        # Change to the repository directory
        os.chdir(repo_path)

        # Stage the files or the entire directory if no specific files provided
        if files_to_commit:
            subprocess.run(["git", "add"] + files_to_commit, check=True)
        else:
            subprocess.run(["git", "add", "."], check=True)  # Add all changes

        # Commit with a timestamp message
        commit_message = f"Data update on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push to the remote repository and set upstream if not already set
        subprocess.run(["git", "push", "--set-upstream", "origin", "master"], check=True)

        print("✅ Git operations completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")
