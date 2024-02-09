import os
import re
import string

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from rich import print

from neogpt.settings.config import (
    AGENT_THOUGHTS,
    CURRENT_WORKING_AGENT,
    QA_ENGINEER_FEEDBACK,
    WORKSPACE_DIRECTORY,
)
from neogpt.prompts.agent_prompt import QA_ENGINEER_PROMPT


class QA_Engineer:
    def __init__(self, llm) -> None:
        self.qa_engineer_prompt = QA_ENGINEER_PROMPT
        self.ai_prefix = "AI: "
        self.user_prefix = "Human: "
        self.llm = llm
        self.agent_thoughts = AGENT_THOUGHTS
        self.role = "QA Engineer 🤖🔎"

    def parse_code(self, code):
        code = "\n".join(code)
        code_pattern = re.compile(r"```python(.*?)```", re.DOTALL)
        matches = re.findall(code_pattern, code)

        file_pattern = re.search(
            r"# filename: (.+\.py)|(\w+\.py)|# (\w+\.py)|# File: (\w+\.py)|# file_name: (.+\.py)|`(.+\.py)`",
            code,
        )
        filename = (
            file_pattern.group(1)
            if (file_pattern and file_pattern.group(1))
            else "main.py"
        )

        # Check if the file already exists in the workspace directory
        base_filename, extension = os.path.splitext(filename)
        suffix = 1
        file_path = os.path.join(WORKSPACE_DIRECTORY, filename)

        while os.path.exists(file_path):
            # If the file exists, append a suffix and construct the new file path
            filename = f"{base_filename}_{suffix}{extension}"
            file_path = os.path.join(WORKSPACE_DIRECTORY, filename)
            suffix += 1

        if len(matches) > 0:
            python_code = matches[0].strip()
            with open(file_path, "w") as f:
                f.write(python_code)
            print(
                "\n"
                + f"[bright_yellow]Your task is been writtern to {WORKSPACE_DIRECTORY}/{filename} [/bright_yellow]"
            )

        return code

    def analyse(self, query):
        global CURRENT_WORKING_AGENT, QA_ENGINEER_FEEDBACK
        CURRENT_WORKING_AGENT.append(str(self.role))

        validation_prompt = PromptTemplate(
            template=self.qa_engineer_prompt,
            input_variables=["question", "latest_thought"],
        )

        self.moderator = LLMChain(
            llm=self.llm,
            prompt=validation_prompt,
        )
        # print(self.agent_thoughts)
        validate = self.moderator.invoke(
            {
                "question": query,
                "latest_thought": self.agent_thoughts[-1],
            }
        )

        if ("CORRECT" in validate["text"] or "TERMINATE" in validate["text"]) and (
            "CORRECT BUT NOT SOLVED" not in validate["text"].strip(string.punctuation)
            or "INCORRECT AND NOT SOLVED"
            not in validate["text"].strip(string.punctuation)
        ):
            self.parse_code(self.agent_thoughts)
            return True
        else:
            # print("INCORRECT")
            QA_ENGINEER_FEEDBACK.append(validate["text"])
            return False
