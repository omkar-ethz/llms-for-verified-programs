"""Interface for LLMs"""
import os
from typing import Literal, Any

import dotenv
import openai
from openai.types.chat import ChatCompletion
import requests # type: ignore
import sagemaker  # type: ignore
from sagemaker.huggingface import HuggingFacePredictor  # type: ignore
from transformers import AutoTokenizer # type: ignore


from data import Data

ModelType = Literal[
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-1106",
    "gpt-4",
    "gpt-3.5-turbo-instruct",
    "gpt-4-turbo-preview",
    "codellama",
    "codellama-base",
    "CodeLlama-7b-Instruct-hf",
    "CodeLlama-13b-Instruct-hf",
    "CodeLlama-34b-Instruct-hf",
    "CodeLlama-70b-Instruct-hf"
]

dotenv.load_dotenv()


class Model:
    """Abstract model class"""

    def __init__(self, name: ModelType):
        self.name = name

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
        examples: list[str] | None = None,
    ) -> Any:
        """Returns a prompt with the solution to hold_out example held out"""

    def get_response(
        self, prompt: Any, seed: int | None = None, temperature=0.0
    ) -> Any:
        """Calls the underlying model and returns the response"""

    def extend_prompt(self, prompt: Any, program_snippet: str, result: str) -> Any:
        """Extends the prompt with another round of {user, verif_error}"""

    def print_and_process_response(self, response: Any) -> str:
        """Print response from GPT and return the program snippet"""
        raise NotImplementedError()


class Chat(Model):
    """Chat model class"""

    def __init__(self, name: ModelType, data: Data):
        super().__init__(name)
        self.data = data
        self.client = openai.OpenAI(api_key=os.getenv("GPT_SECRET_KEY"), timeout=120)

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
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
                        "content": self._get_user_message(key, example),
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
                "content": self._get_user_message(key, hold_out)
                # + "\n# Remember: from this point on think step by step and \
                # show your work as python comments before producing the verified program\n",
            }
        )
        return messages

    def _get_user_message(self, key: str, example: str) -> str:
        """Get message for role user"""
        content_user = self.data.get_example(key, example, "unverified")
        content_user += f"\n{self.data.get_cached_result(key, example)}"
        return content_user

    def get_response(
        self, prompt, seed: int | None = None, temperature=0.0
    ) -> ChatCompletion:
        return self.client.chat.completions.create(
            model=self.name,
            messages=prompt,
            seed=seed,
            temperature=temperature,
            max_tokens=1024,
        )

    def extend_prompt(
        self, prompt: list[dict[str, str]], program_snippet: str, result: str
    ) -> list[dict[str, str]]:
        prompt.append({"role": "assistant", "content": program_snippet})
        user_message = (
            result if (self.name == "gpt-4" or self.name == "gpt-4-turbo-preview") else program_snippet + "\n" + result
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
        if program_snippet.startswith("```python"):
            program_snippet = self._extract_from_markdown(program_snippet)
        print("Generated program from GPT:")
        print(program_snippet)
        print("=====================================")
        return program_snippet
    
    def _extract_from_markdown(self, wrapped_program: str) -> str:
        """Extracts the program snippet from the markdown"""
        program_snippet = wrapped_program.split("```python")[1].split("```")[0].strip()
        return program_snippet

    def process_response(self, response: ChatCompletion) -> str:
        """Returns the program snippet from the response"""
        program_snippet = response.choices[0].message.content
        if program_snippet is None:
            program_snippet = "Empty response from GPT"
        return program_snippet


class Completion(Model):
    """Completion model class"""

    def __init__(self, name: ModelType, data: Data):
        super().__init__(name)
        self.data = data
        self.client = openai.OpenAI(api_key=os.getenv("GPT_SECRET_KEY"), timeout=120)

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
        examples: list[str] | None = None,
    ) -> str:
        examples = self.data.get_list_of_examples(key)
        messages = (
            f"<task-description>\n{self.data.get_system_prompt()}</task-description>\n"
        )
        for example in examples:
            if example != hold_out:
                messages += f"<unverified>\n{self._get_user_message(key, example)}</unverified>\n"
                messages += f"<verified>\n{self.data.get_example(key, example, 'verified')}</verified>\n"
        messages += (
            f"<unverified>\n{self._get_user_message(key, hold_out)}</unverified>\n"
        )
        messages += "<verified>\n#Let's think step by step\n"
        return messages

    def _get_user_message(self, key: str, example: str) -> str:
        """Get message for role user"""
        content_user = self.data.get_example(key, example, "unverified")
        content_user += f"\n{self.data.get_cached_result(key, example)}"
        return content_user

    def get_response(
        self, prompt, seed: int | None = None, temperature=0.0
    ) -> openai.types.Completion:
        return self.client.completions.create(
            model=self.name,
            prompt=prompt,
            max_tokens=500,
            suffix="</verified>",
        )

    def extend_prompt(self, prompt: str, program_snippet: str, result: str) -> str:
        prompt += f"<unverified>\n{program_snippet}\n{result}\n</unverified>\n"
        prompt += "<verified>\n#Let's think step by step\n"
        return prompt

    def print_and_process_response(self, response: openai.types.Completion) -> str:
        program_snippet = response.choices[0].text
        print("Generated program from GPT:")
        print(program_snippet)
        print("=====================================")
        return program_snippet


class LlamaModel(Model):
    """CodeLlama model class"""

    def __init__(self, name: ModelType, data: Data, predictor_endpoint: str):
        super().__init__(name)
        self.data = data
        if predictor_endpoint != "test":
            sess = sagemaker.Session()
            self.predictor = HuggingFacePredictor(
                endpoint_name=predictor_endpoint, sagemaker_session=sess
            )

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
        examples: list[str] | None = None,
    ) -> str:
        if examples is None:
            examples = self.data.get_list_of_examples(key)
        messages = f"{self.data.get_system_prompt()}\n"
        for example in examples:
            if example != hold_out:
                messages += f"### Unverified program:\n{self.data.get_example(key, example, "unverified")}\n\n"
                messages += f"### Verification error:\n{self.data.get_cached_result(key, example)}\n\n"
                messages += f"### Verified program:\n{self.data.get_example(key, example, "verified")}\n\n"
        messages += f"### Unverified program:\n{self.data.get_example(key, hold_out, "unverified")}\n\n"
        messages += f"### Verification error:\n{self.data.get_cached_result(key, hold_out)}\n\n"
        messages += "### Verified program:\n"
        return messages

    def get_response(
        self, prompt: str, seed: int | None = None, temperature: float = 0.7, **kwargs
    ) -> str:
        max_new_tokens = kwargs.pop("max_new_tokens", 320)

        #pretrained model:
        if self.name == "codellama-base":
            output = self.predictor.predict(
            {
                "inputs": prompt,
                "parameters": {
                    "do_sample": True,
                    "temperature": temperature,
                    "max_new_tokens": max_new_tokens,
                    "return_full_text": False,
                    # "top_p": 0.7,
                    # "top_k": 50,
                    # "repetition_penalty": 1,
                },
            })
            output = output[0]["generated_text"]
            if "### Unverified program:" in output:
                output = output.split("### Unverified program:")[0].strip()
            elif "###" in output:
                output = output.split("###")[0].strip()
            return output

        # fine-tuned model:
        return self.predictor.predict(
            {
                "inputs": prompt,
                "params": {
                    "max_new_tokens": max_new_tokens,
                    "do_sample": True,
                    "temperature": temperature,
                    **kwargs
                    # "top_p": 0.7,
                    # "top_k": 50,
                    # "repetition_penalty": 1,
                },
                "decode_params": {
                    "skip_special_tokens": True,
                },
            }
        )

    def extend_prompt(self, prompt: str, program_snippet: str, result: str) -> str:
        """For CodeLlama, this is really replace prompt with program snippet and verification result"""
        if self.name == "codellama-base":
            prompt += f"{program_snippet}\n\n"
        else:
            prompt = f"{self.data.get_system_prompt()}\n"
        prompt += f"### Unverified program:\n{program_snippet}\n\n"
        prompt += f"### Verification error:\n{result}\n\n"
        prompt += "### Verified program:\n"
        return prompt

    def print_and_process_response(self, response: str) -> str:
        program_snippet = response
        print("Generated program from model:")
        print(program_snippet)
        print("=====================================")
        return program_snippet


class CodeLlamaInstruct(Model):
    """CodeLlama Instruct Model (7B, 13B, 34B) hosted on TogetherAI"""
    
    def __init__(self, name: ModelType, data: Data):
        super().__init__(name)
        self.data = data
        self.tokenizer = AutoTokenizer.from_pretrained(f"codellama/{name}")

    def get_prompt(
        self,
        hold_out: str,
        key: str = "list",
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
                        "content": self._get_user_message(key, example),
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
                "content": self._get_user_message(key, hold_out)
            }
        )
        return messages

    def _get_user_message(self, key: str, example: str) -> str:
        """Get message for role user"""
        content_user = self.data.get_example(key, example, "unverified")
        content_user += f"\n{self.data.get_cached_result(key, example)}"
        # content_user += "\n#Remember: return only the verified program without any explanation or wrapping"
        return content_user

    def get_response(
        self, prompt: list[dict[str, str]], seed: int | None = None, temperature: float = 0.7, **kwargs
    ) -> str:
        prompt_str = self.tokenizer.apply_chat_template(prompt, tokenize=False)
        url = "https://api.together.xyz/v1/completions"
        payload = {
            "model": f"codellama/{self.name}",
            "prompt": prompt_str,
            "max_tokens": 320,
            "stop": ["</s>", "<step>"],
            "temperature": temperature,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "Bearer f0d9c7f9871c9b518999b0b5552ff9b2257abf8445d74f6e3d8c21a7a80ff7a4"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=120)
        # throw exception if status not 200
        response.raise_for_status()
        response = response.json()
        return response['choices'][0]['text'].strip()

    def extend_prompt(
        self, prompt: list[dict[str, str]], program_snippet: str, result: str
    ) -> list[dict[str, str]]:
        prompt.append({"role": "assistant", "content": program_snippet})
        user_message = program_snippet + "\n" + result
        # user_message += "\n#Remember: return only the verified program without any explanation or wrapping"
        prompt.append(
            {
                "role": "user",
                "content": user_message,
            }
        )
        return prompt

    def print_and_process_response(self, response: str) -> str:
        program_snippet = response
        print(f"Generated program from {self.name}:")
        print(program_snippet)
        print("=====================================")
        return program_snippet


def get_model(
    model_type: ModelType, data: Data, predictor_endpoint: str | None = None
) -> Model:
    """Returns the model object for the given model_type"""
    if model_type in ["CodeLlama-7b-Instruct-hf", "CodeLlama-13b-Instruct-hf", "CodeLlama-34b-Instruct-hf", "CodeLlama-70b-Instruct-hf"]:
        return CodeLlamaInstruct(model_type, data)
    if model_type == "codellama" or model_type == "codellama-base":
        assert predictor_endpoint is not None
        return LlamaModel(model_type, data, predictor_endpoint)
    if model_type == "gpt-3.5-turbo-instruct":
        return Completion(model_type, data)
    return Chat(model_type, data)
