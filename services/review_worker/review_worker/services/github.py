from github import Github
from review_worker.config import Settings

class GitHubService:
    def __init__(self, settings: Settings):
        # In a real app, you might handle App Installation Tokens here
        self.client = Github(settings.GITHUB_API_TOKEN)

    def get_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """Fetches the raw diff string for the PR."""
        repo = self.client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        # We can get files specifically to avoid huge diffs
        diff_text = ""
        for file in pr.get_files():
            if file.status != "removed" and file.filename.endswith(".py"):
                diff_text += f"\n--- File: {file.filename} ---\n"
                diff_text += file.patch or ""
        
        return diff_text

    def post_comment(self, repo_name: str, pr_number: int, comment: str):
        repo = self.client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)