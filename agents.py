from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from workflow.config import READER_SUMMARY_WORDS

load_dotenv()

# ==========================================================
# LLM
# ==========================================================

llm = ChatMistralAI(
    model="mistral-medium-latest",
    temperature=0,
)

# ==========================================================
# Reader Chain
# ==========================================================

reader_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
You are an expert research analyst.

Produce a structured summary with the following sections:

Overview

Important Facts

Statistics

Recent Developments

Key Takeaways

Rules:

- Do NOT invent information.
- Preserve important statistics.
- Preserve dates.
- Preserve names.
- Preserve technical details.
- Ignore navigation menus, ads and irrelevant text.
- Write approximately {READER_SUMMARY_WORDS} words.

At the end include:

Key Points:
- ...
- ...
- ...
"""
        ),
        (
            "human",
            """
Title:
{title}

URL:
{url}

Content:

{content}
"""
        )
    ]
)

reader_chain = reader_prompt | llm | StrOutputParser()

# ==========================================================
# Writer Chain
# ==========================================================

writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert research report writer.

Your job is to convert the supplied research into a professional report.

Rules:
- Write in a formal tone.
- Never invent facts.
- Use only the supplied research.
- Organize the report properly.
- Mention important statistics whenever available.
- Include the source URL(s) at the end.
- If multiple sources mention the same fact, state it only once.
""",
        ),
        (
            "human",
            """
Topic:
{topic}

The following research consists of summaries extracted from several reliable sources.

Combine them into one coherent research report.

Requirements:

- Merge similar findings.
- Remove repetition.
- Mention disagreements if any.
- Keep all important statistics.
- Preserve technical terminology.
- Write professionally.
- Cite every URL under Sources.

Research:

{research}

Write a detailed report with the following sections:

# Introduction

# Key Findings
(Minimum 3 detailed findings)

# Analysis

# Conclusion

# Sources
(List every URL found in the research)
""",
        ),
    ]
)

writer_chain = (
    writer_prompt
    | llm
    | StrOutputParser()
)

# ==========================================================
# Critic Chain
# ==========================================================

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert research reviewer.

Evaluate the report critically.

Consider:

- Accuracy
- Completeness
- Organization
- Readability
- Missing information
- Citation quality

Be constructive.
""",
        ),
        (
            "human",
            """
Review the following report.

{report}

Return exactly in this format:

Score: X/10

Strengths
- ...
- ...

Weaknesses
- ...
- ...

Suggestions
- ...
- ...

Overall Verdict
...
""",
        ),
    ]
)

critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)