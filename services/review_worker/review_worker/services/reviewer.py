from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class ReviewerAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def analyze_code(self, diff: str) -> str:
        """
        Uses the LLM to find bugs in the diff.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a Senior Python Backend Engineer doing a code review.
                    Analyze the provided git diff.
                    Rules:
                    1. Ignore formatting/whitespace changes.
                    2. Focus on Logic Bugs, Security Risks (SQLi, XSS), and Performance issues.
                    3. Be concise and provide code snippets for fixes.
                    4. If the code looks good, reply with "LGTM! 🚀".
                    """,
                ),
                ("user", "Here is the diff:\n\n{diff}"),
            ]
        )

        chain = prompt | self.llm
        result = await chain.ainvoke({"diff": diff})
        return str(result.content)
