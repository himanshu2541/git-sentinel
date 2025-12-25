import logging
import httpx
from gidgethub.httpx import GitHubAPI
from review_worker.config import Settings

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self, settings: Settings):
        self.token = settings.GITHUB_API_TOKEN
        self.app_name = settings.APP_NAME
        
    async def get_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """
        Async fetches the PR files and constructs a diff string.
        """
        async with httpx.AsyncClient() as client:
            gh = GitHubAPI(client, self.app_name, oauth_token=self.token)
            
            # API: GET /repos/{owner}/{repo}/pulls/{pull_number}/files
            # This returns the list of files with their patches
            try:
                files = await gh.getitem(f"/repos/{repo_name}/pulls/{pr_number}/files")
            except Exception as e:
                logger.error(f"Failed to fetch PR files: {e}")
                return ""

            diff_text = ""
            for file in files:
                # Same logic as your PyGithub code
                filename = file.get("filename", "")
                status = file.get("status", "")
                patch = file.get("patch", "")

                if status != "removed" and filename.endswith(".py"):
                    diff_text += f"\n--- File: {filename} ---\n"
                    diff_text += patch
            
            return diff_text

    async def post_comment(self, repo_name: str, pr_number: int, comment: str):
        """
        Async posts a comment to the PR.
        """
        async with httpx.AsyncClient() as client:
            gh = GitHubAPI(client, self.app_name, oauth_token=self.token)
            
            # API: POST /repos/{owner}/{repo}/issues/{issue_number}/comments
            # Note: GitHub PRs are technically "issues" for commenting purposes
            await gh.post(
                f"/repos/{repo_name}/issues/{pr_number}/comments",
                data={"body": comment}
            )