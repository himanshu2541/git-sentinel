import json
import asyncio
import logging
from shared.providers.redis import RedisFactory
from review_worker.providers.llm import LLMFactory
from review_worker.config import Settings, settings
from shared.logging import setup_logging

# Services
from review_worker.services.github import GitHubService
from review_worker.services.reviewer import ReviewerAgent

setup_logging()
logger = logging.getLogger("Review-Worker")

async def main():
    logger.info("Starting GitSentinel Worker...")
    
    # Initialize Dependencies (Reusing your patterns)
    redis = RedisFactory.get_client(settings)
    llm = LLMFactory.get_llm(settings)
    
    github_service = GitHubService(settings)
    reviewer = ReviewerAgent(llm)

    logger.info("Listening for PRs on 'review_jobs'...")

    while True:
        try:
            # Blocking pop from Redis
            result = await redis.brpop(["review_jobs"], timeout=2)  # type: ignore
            
            if result:
                _, data = result
                job = json.loads(data)
                
                repo = job["repo_name"]
                pr_id = job["pr_number"]
                
                logger.info(f"Analyzing PR #{pr_id} in {repo}...")
                
                # Fetch Diff
                diff_text = github_service.get_pr_diff(repo, pr_id)
                if not diff_text:
                    logger.info("No relevant code changes found.")
                    continue

                # AI Review
                review_comments = await reviewer.analyze_code(diff_text)
                
                # Post Feedback
                if review_comments:
                    formatted_msg = f"## GitSentinel Review\n\n{review_comments}"
                    github_service.post_comment(repo, pr_id, formatted_msg)
                    logger.info(f"Posted review for PR #{pr_id}")

        except Exception as e:
            logger.error(f"Error processing job: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())