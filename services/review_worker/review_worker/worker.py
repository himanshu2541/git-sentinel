import json
import asyncio
import logging
from shared.providers.redis import RedisFactory
from review_worker.providers.llm import LLMFactory
from review_worker.config import settings
from shared.logging import setup_logging

# Services
from review_worker.services.github import GitHubService
from review_worker.services.reviewer import ReviewerAgent

setup_logging()
logger = logging.getLogger("Review-Worker")

async def main():
    logger.info("Starting GitSentinel Worker...")

    # Initialize Dependencies
    redis = RedisFactory.get_client(settings)
    llm = LLMFactory.get_llm(settings)

    github_service = GitHubService(settings)
    reviewer = ReviewerAgent(llm)

    logger.info("Listening for PRs on 'review_jobs'...")

    while True:
        try:
            # Blocking pop from Redis is already async-safe in aioredis
            result = await redis.brpop(["review_jobs"], timeout=2)  # type: ignore

            if result:
                _, data = result
                job = json.loads(data)

                repo = job.get("repo_name", "Unknown Repo")
                pr_id = job.get("pr_number", 0)
                source = job.get("source", "github")

                # Broadcast START
                await redis.publish("sentinel_events", json.dumps({
                    "type": "log", 
                    "message": f"Picked up {source.upper()} job for {repo}"
                }))

                diff_text = ""

                # Fetch Code (GitHub or Manual)
                if source == "manual":
                    diff_text = job.get("code", "")
                    logger.info("Processing manual code review request.")
                else:
                    logger.info(f"Analyzing PR #{pr_id} in {repo}...")
                    try:
                        diff_text = await github_service.get_pr_diff(repo, pr_id)
                    except Exception as e:
                        logger.error(f"GitHub Fetch Failed: {e}")
                        await redis.publish("sentinel_events", json.dumps({
                            "type": "error", "message": f"GitHub Error: {str(e)}"
                        }))
                        continue

                if not diff_text:
                    logger.info("No relevant code changes found.")
                    await redis.publish("sentinel_events", json.dumps({
                        "type": "log", "message": "No code changes found to analyze."
                    }))
                    continue

                # Broadcast ANALYZING
                await redis.publish("sentinel_events", json.dumps({
                    "type": "log",
                    "message": "Analyzing code logic...",
                }))

                # AI Review
                review_comments = await reviewer.analyze_code(diff_text)

                if review_comments:
                    formatted_msg = f"## GitSentinel Review\n\n{review_comments}"
                    
                    # Handle Output (Post to GitHub OR just Log)
                    if source == "github":
                        await github_service.post_comment(repo, pr_id, formatted_msg)
                        logger.info(f"Posted review for PR #{pr_id}")
                    
                    # Broadcast SUCCESS (Payload includes the full review for Frontend)
                    await redis.publish("sentinel_events", json.dumps({
                        "type": "success",
                        "repo": repo,
                        "pr": pr_id,
                        "message": "Analysis Complete!",
                        "review": review_comments # Frontend can optionally display this
                    }))

        except Exception as e:
            logger.error(f"Error processing job: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())