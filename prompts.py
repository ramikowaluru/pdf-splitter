SUMMARY_PROMPT_ANTHROPIC_OPENAI = """
Here is the chapter text to rewrite for individuals with dyslexia:

<chapter_text>
{text}
</chapter_text>

Please rewrite the chapter text following these guidelines:

1. Use simple, clear, and concise language.
2. Break down complex concepts into smaller, manageable parts. 
3. Utilize bullet points, numbered lists, and short paragraphs to improve readability.
4. Include suggestions for visual aids (e.g., diagrams, illustrations, or flowcharts) to support understanding, described within [Visual Aid: ...] brackets.
5. Emphasize key terms, definitions, and important concepts using *bold text*.
6. Provide explicit connections between ideas and concepts to maintain coherence.
7. Offer examples and analogies to relate new information to familiar concepts.
8. Maintain the core information and learning objectives of the original chapter.

Before rewriting, use the scratchpad to plan out how you will restructure and simplify the content:

<scratchpad>
(Plan your rewrite here, breaking down the process into steps if needed)
</scratchpad>

Now, rewrite the chapter text according to the guidelines and your plan. Ensure the rewritten content is comprehensive and does not omit essential information. If the rewritten content exceeds the token limit, prioritize the most critical information and concepts.

After rewriting the chapter, generate a list of questions to check the reader's understanding. Include a mix of easy, medium, and complex questions. Format the questions like this:

<questions>
Easy:
1. [Question 1]
2. [Question 2] 
...

Medium:
1. [Question 1]
2. [Question 2]
...

Complex: 
1. [Question 1]
2. [Question 2]
...
</questions>

Generate as many questions as possible within the token limit to thoroughly assess the reader's comprehension of the rewritten chapter.
"""

SUMMARY_PROMPT_GEMINI = """
Here is a chapter from a textbook. Please rewrite it to make it easier for people with dyslexia to understand.

<chapter_text>
{text}
</chapter_text>

Here's how to rewrite it:

1.  **Simplify language:** Use shorter sentences and everyday words.
2.  **Break down ideas:** Explain complex ideas step-by-step.
3.  **Use visuals:** Suggest pictures, diagrams, or charts to help explain ideas. [Visual Aid: ...]
4.  **Highlight important stuff:** Use **bold** for key words and ideas.
5.  **Connect ideas:** Show how different ideas relate to each other.
6.  **Give examples:** Use real-life examples to make things clearer.
7.  **Keep it short:** Focus on the most important information.

After you rewrite the chapter, please write some questions to check if the reader understands. Include easy, medium, and hard questions.

<questions>
Easy:
1. [Question 1]
2. [Question 2] 
...

Medium:
1. [Question 1]
2. [Question 2]
...

Complex: 
1. [Question 1]
2. [Question 2]
...
</questions>
"""