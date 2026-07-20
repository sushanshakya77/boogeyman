import subprocess


def get_diff(repo: str = ".", staged: bool = False) -> str:
    args = ["git", "-C", repo, "diff", "--unified=3"]
    if staged:
        args.append("--cached")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return result.stdout
