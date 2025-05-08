import subprocess
import os

def update_repo(repo_path="data/tinygrad"):
    parent_dir = os.path.dirname(repo_path)
    if not os.path.exists(parent_dir): os.makedirs(parent_dir)
    if not os.path.exists(repo_path): subprocess.run(["git", "clone", "https://github.com/tinygrad/tinygrad.git", repo_path])
    else: subprocess.run(["git", "pull"], cwd=repo_path)

    local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path).decode("utf-8").strip()
    remote_hash = subprocess.check_output(["git", "rev-parse", "origin/master"], cwd=repo_path).decode("utf-8").strip()
    if local_hash != remote_hash:
        print(f"Updating {repo_path} from {local_hash} to {remote_hash}")
    else: print(f"No updates for {repo_path}")

