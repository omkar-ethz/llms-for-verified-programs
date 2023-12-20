"""Interface for LLMs"""
import os
from typing import Literal, Any

import dotenv
import openai
from openai.types.chat import ChatCompletion

from data import Data

GPTModel = Literal[
    "gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4", "gpt-3.5-turbo-instruct"
]

dotenv.load_dotenv()
client = openai.OpenAI(api_key=os.getenv("GPT_SECRET_KEY"), timeout=120)


class Model:
    """Abstract model class"""

    def __init__(self, name: GPTModel):
        self.name = name

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
        with_errors: bool = True,
    ) -> Any:
        """Returns a prompt with the solution to hold_out example held out"""

    def get_response(self, prompt, seed: int | None = None) -> Any:
        """Calls the underlying model and returns the response"""

    def extend_prompt(self, prompt: Any, program_snippet: str, result: str):
        """Extends the prompt with another round of {user, verif_error}"""

    def print_and_process_response(self, response: Any) -> str:
        """Print response from GPT and return the program snippet"""
        raise NotImplementedError()


class Chat(Model):
    """Chat model class"""

    def __init__(self, name: GPTModel, data: Data):
        super().__init__(name)
        self.data = data

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
        with_errors: bool = True,
        examples: list[str] | None = None,
    ) -> list[dict[str, str]]:
        if examples is None:
            examples = self.data.get_list_of_examples(key)
        messages = [{"role": "system", "content": self.data.get_system_prompt()}]
        for example in examples:
            if example != hold_out:
                messages.append(
                    {
                        "role": "user",
                        "content": self._get_user_message(key, example, with_errors),
                    }
                )
                messages.append(
                    {
                        "role": "assistant",
                        "content": self.data.get_example(key, example, "verified"),
                    }
                )
        messages.append(
            {
                "role": "user",
                "content": self._get_user_message(key, hold_out, with_errors)
                # + "\n# Remember: from this point on think step by step and \
                # show your work as python comments before producing the verified program\n",
            }
        )
        return messages

    def _get_user_message(self, key: str, example: str, with_errors: bool):
        """Get message for role user"""
        content_user = self.data.get_example(key, example, "unverified")
        if with_errors:
            content_user += f"\n{self.data.get_cached_result(key, example)}"
        return content_user

    def get_response(self, prompt, seed: int | None = None, temperature=0.0):
        return client.chat.completions.create(
            model=self.name, messages=prompt, seed=seed, temperature=temperature
        )

    def extend_prompt(
        self, prompt: list[dict[str, str]], program_snippet: str, result: str
    ):
        prompt.append({"role": "assistant", "content": program_snippet})
        user_message = (
            result if self.name == "gpt-4" else program_snippet + "\n" + result
        )
        prompt.append(
            {
                "role": "user",
                "content": user_message,
            }
        )
        return prompt

    def print_and_process_response(self, response: ChatCompletion) -> str:
        program_snippet = response.choices[0].message.content
        if program_snippet is None:
            program_snippet = "Empty response from GPT"
        print("Generated program from GPT:")
        print(program_snippet)
        print("=====================================")
        return program_snippet

    def process_response(self, response: ChatCompletion) -> str:
        """Returns the program snippet from the response"""
        program_snippet = response.choices[0].message.content
        if program_snippet is None:
            program_snippet = "Empty response from GPT"
        return program_snippet


class Completion(Model):
    """Completion model class"""

    def __init__(self, name: GPTModel, data: Data):
        super().__init__(name)
        self.data = data

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
        with_errors: bool = True,
    ) -> str:
        examples = self.data.get_list_of_examples(key)
        messages = (
            f"<task-description>\n{self.data.get_system_prompt()}</task-description>\n"
        )
        for example in examples:
            if example != hold_out:
                messages += f"<unverified>\n{self._get_user_message(key, example, with_errors)}</unverified>\n"
                messages += f"<verified>\n{self.data.get_example(key, example, 'verified')}</verified>\n"
        messages += f"<unverified>\n{self._get_user_message(key, hold_out, with_errors)}</unverified>\n"
        messages += "<verified>\n#Let's think step by step\n"
        return messages

    def _get_user_message(self, key: str, example: str, with_errors: bool):
        """Get message for role user"""
        content_user = self.data.get_example(key, example, "unverified")
        if with_errors:
            content_user += f"\n{self.data.get_cached_result(key, example)}"
        return content_user

    def get_response(self, prompt, seed: int | None = None):
        return client.completions.create(
            model=self.name,
            prompt=prompt,
            max_tokens=500,
            suffix="</verified>",
        )

    def extend_prompt(self, prompt: str, program_snippet: str, result: str):
        prompt += f"<unverified>\n{program_snippet}\n{result}\n</unverified>\n"
        prompt += "<verified>\n#Let's think step by step\n"
        return prompt

    def print_and_process_response(self, response: openai.types.Completion) -> str:
        program_snippet = response.choices[0].text
        print("Generated program from GPT:")
        print(program_snippet)
        print("=====================================")
        return program_snippet


def get_model(model_type: GPTModel, data: Data) -> Model:
    """Returns the model object for the given model_type"""
    if model_type == "gpt-3.5-turbo-instruct":
        return Completion(model_type, data)
    return Chat(model_type, data)
