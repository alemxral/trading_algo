from git import Repo, GitCommandError
from datetime import datetime
import os

def commit_and_push(files_to_commit=None, repo_path="."):
    """
    Stage, commit, and push changes using GitPython.

    Args:
        files_to_commit (list): List of file paths to commit. If None, commits the entire directory.
        repo_path (str): Path to the local Git repository (default: current directory).
    """
    try:
        print("\n🔄 Starting Git operations...")

        # Open the existing Git repository
        repo = Repo(repo_path)

        # Stage the files or the entire directory if no specific files provided
        if files_to_commit:
            repo.index.add(files_to_commit)
        else:
            repo.git.add(A=True)  # Add all changes

        # Commit with a timestamp message
        commit_message = f"Data update on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        repo.index.commit(commit_message)

        # Set upstream branch if not already set
        if repo.active_branch.tracking_branch() is None:
            repo.git.push('--set-upstream', 'origin', repo.active_branch.name)

        # Push to the remote repository
        origin = repo.remote(name='origin')
        origin.push(refspec=f'{repo.active_branch.name}:{repo.active_branch.name}', force=True)

        print("✅ Git operations completed successfully.")

    except GitCommandError as e:
        print(f"[ERROR] Git operation failed: {e}")