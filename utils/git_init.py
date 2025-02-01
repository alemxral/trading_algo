from git import Repo
import os

# --- Repository Setup ---
def initialize_git_repo(repo_path='.', remote_url=None):
    """
    Initialize a new Git repository and optionally add a remote.

    Args:
        repo_path (str): Path where the Git repository will be initialized.
        remote_url (str): Optional Git remote repository URL (e.g., GitHub URL).
    """
    try:
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        # Check if .git already exists
        if os.path.exists(os.path.join(repo_path, ".git")):
            print(f"⚠️ Git repository already initialized at {repo_path}")
            return

        # Initialize the Git repository
        repo = Repo.init(repo_path)
        print(f"✅ Initialized new Git repository in {repo_path}")

        # Optional: Add a remote origin
        if remote_url:
            origin = repo.create_remote('origin', remote_url)
            print(f"🔗 Added remote origin: {origin.url}")

    except Exception as e:
        print(f"[ERROR] Failed to initialize repository: {e}")

# --- Usage ---
# Replace with your local path and remote URL
initialize_git_repo(repo_path=r"C:\Users\pc\Algo\trading_algo", remote_url='https://github.com/alemxral/trading_algo.git')
