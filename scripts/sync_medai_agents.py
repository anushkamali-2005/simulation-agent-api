#!/usr/bin/env python3
"""
Utility script to sync the local Agent 2 Simulation folder into the
medai_agents GitHub repository, commit the changes, and optionally push.

Usage (from repo root):
    python scripts/sync_medai_agents.py --push
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_URL = "https://github.com/anushkamali-2005/medai_agents.git"
DEFAULT_SOURCE_DIR = "agents/agent_2_simulation"
DEFAULT_EXTERNAL_DIR = "external_repos/medai_agents"
DEFAULT_TARGET_SUBDIR = "agents/agent_2_simulation"


def run(cmd: list[str], cwd: Path | None = None) -> str:
    """Run a shell command and return stdout or raise on failure."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command {' '.join(cmd)} failed with code {result.returncode}:\n"
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def _remote_branch_exists(repo_dir: Path, branch: str) -> bool:
    """Check whether the remote branch exists."""
    result = run(["git", "ls-remote", "--heads", "origin", branch], cwd=repo_dir)
    return bool(result.strip())


def ensure_repo(repo_dir: Path, repo_url: str, branch: str) -> None:
    """Clone the repo if needed and ensure the target branch is checked out."""
    if repo_dir.exists():
        print(f"[sync] Using existing repo at {repo_dir}")
    else:
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        print(f"[sync] Cloning {repo_url} -> {repo_dir}")
        run(["git", "clone", repo_url, str(repo_dir)])

    run(["git", "fetch", "origin"], cwd=repo_dir)

    # Checkout (create if necessary for empty repos)
    try:
        run(["git", "checkout", branch], cwd=repo_dir)
    except RuntimeError:
        print(f"[sync] Branch {branch} missing; creating it.")
        run(["git", "checkout", "-b", branch], cwd=repo_dir)

    if _remote_branch_exists(repo_dir, branch):
        run(["git", "pull", "origin", branch], cwd=repo_dir)
    else:
        print(f"[sync] Remote branch {branch} does not exist yet; skipping pull.")


def sync_folder(source: Path, destination: Path) -> None:
    """Replace destination folder with source contents."""
    if destination.exists():
        print(f"[sync] Removing existing {destination}")
        shutil.rmtree(destination)

    print(f"[sync] Copying {source} -> {destination}")
    shutil.copytree(source, destination)


def commit_and_push(repo_dir: Path, target_subdir: str, message: str, push: bool, branch: str) -> bool:
    """Stage, commit, and optionally push changes."""
    run(["git", "add", target_subdir], cwd=repo_dir)
    status = run(["git", "status", "--porcelain"], cwd=repo_dir)

    if not status:
        print("[sync] No changes detected; skipping commit.")
        return False

    run(["git", "commit", "-m", message], cwd=repo_dir)
    print(f"[sync] Commit created with message: {message}")

    if push:
        run(["git", "push", "origin", branch], cwd=repo_dir)
        print("[sync] Changes pushed to remote.")

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Agent 2 folder into medai_agents repo.")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="Target GitHub repo URL.")
    parser.add_argument("--source-dir", default=DEFAULT_SOURCE_DIR, help="Path to local agent folder.")
    parser.add_argument("--repo-dir", default=DEFAULT_EXTERNAL_DIR, help="Local path for cloned repo.")
    parser.add_argument("--target-subdir", default=DEFAULT_TARGET_SUBDIR, help="Destination path inside repo.")
    parser.add_argument("--branch", default="main", help="Branch to commit to.")
    parser.add_argument("--commit-message", default="Sync agent_2_simulation folder", help="Commit message.")
    parser.add_argument("--push", action="store_true", help="Push changes after committing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_dir = Path(args.repo_dir).resolve()
    source_dir = Path(args.source_dir).resolve()
    destination_dir = repo_dir / args.target_subdir

    if not source_dir.exists():
        print(f"[sync] Source directory not found: {source_dir}")
        return 1

    try:
        ensure_repo(repo_dir, args.repo_url, args.branch)
        sync_folder(source_dir, destination_dir)
        changes = commit_and_push(
            repo_dir=repo_dir,
            target_subdir=args.target_subdir,
            message=args.commit_message,
            push=args.push,
            branch=args.branch,
        )
    except Exception as exc:
        print(f"[sync] Error: {exc}")
        return 1

    if not changes:
        print("[sync] Repository already up to date.")
    else:
        print("[sync] Sync completed successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

