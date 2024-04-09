"""Contains functions to get various prompt combinations"""
# import random
import time
from typing import Literal
import dataclasses
import openai
from requests import HTTPError # type: ignore
import data
import nagini_client as nagini
import model


@dataclasses.dataclass
class EvalResult:
    """Class to store the results of the evaluation"""

    results: dict[str, bool | Literal["Error"]] = dataclasses.field(
        default_factory=dict
    )
    verified_at: dict[str, tuple[int, int]] = dataclasses.field(default_factory=dict)


class Evaluation:
    """Evaluations of model on dataset specified in config_file"""

    def __init__(
        self,
        dataset: data.Data,
        model_str: model.ModelType = "gpt-3.5-turbo-1106",
        predictor_endpoint: str | None = None,
    ):
        self.data = dataset
        self.model = model.get_model(
            model_str, self.data, predictor_endpoint=predictor_endpoint
        )

    @classmethod
    def from_config(
        cls, config_file: str, model_str: model.ModelType = "gpt-3.5-turbo-1106"
    ):
        """Creates an evaluation from the given config file"""
        return cls(data.Data(config_file), model_str)

    def verify_program_snippet(
        self, key: str, program_snippet: str, method_name: str | None = None
    ) -> nagini.VerificationResult:
        """Expects: response contains a candidate program generated by assistant\n
        Sends the program to Nagini and returns the verification result"""
        (
            program_file,
            combined_length,
        ) = self.data.combine_method_with_declaration_and_dependencies(
            key, program_snippet, method_name
        )
        program_length = len(program_snippet.split("\n"))
        offset = combined_length - program_length
        result = nagini.verify(program_file)
        for i, line_no in enumerate(result.line_no):
            result.line_no[i] = self._get_relative_line_number(line_no, offset)
        return result

    def _get_relative_line_number(self, line_no: str, offset: int) -> str:
        """Returns the line number relative to the method"""
        if "no position" in line_no:
            return line_no
        line, column = line_no.split(".")
        rel_line = int(line) - offset
        return f"{rel_line}.{column}"

    def run_eval(
        self,
        k=1,
        n=1,
        key="list",
    ) -> EvalResult:
        """Runs the evaluation for all examples in the list of examples for the given key\n"""
        examples = self.data.get_list_of_examples(key)
        eval_result = EvalResult()
        for example in examples:
            result, verified_at, _ = self.run_example(example, k, n, key)
            eval_result.results[example] = result
            if verified_at is not None:
                eval_result.verified_at[example] = verified_at
        return eval_result

    def run_example(
        self, example: str, k=1, n=1, key="list", examples=None
    ) -> tuple[bool | Literal["Error"], tuple[int, int] | None, str]:
        """Runs the evaluation for a single given example"""
        result: bool | Literal["Error"]
        verified_at: tuple[int, int] | None = None
        # rand = random.Random(42)
        for i in range(k):
            # seed = rand.randint(12345, 54321)
            prompt = self.model.get_prompt(example, key=key, examples=examples)
            for j in range(n):
                print(
                    "Running example:",
                    example,
                    "; attempt:",
                    i + 1,
                    "; error depth:",
                    j + 1,
                )
                try:
                    temperature = min(1.5, 0.1 + 0.5 * i) # schedule for codellama
                    if self.model.name == "gpt-4-turbo-preview":
                        temperature = min(1.0, 0.4 * i) # schedule for GPT-4
                    print("Using temperature:", temperature)
                    response = self.model.get_response(
                        prompt, seed=None, temperature=temperature
                    )
                except openai.APITimeoutError as e:
                    result = "Error"
                    print("Timeout error!", e)
                    time.sleep(5)
                    continue
                except HTTPError as e:
                    result = "Error"
                    print("HTTP error!", e)
                    time.sleep(5)
                    continue
                program_snippet = self.model.print_and_process_response(response)
                verif_result = self.verify_program_snippet(key, program_snippet, method_name=example)
                print("Verification result:\n", verif_result, "\n\n")
                result = verif_result.status == "Verification successful"
                if result:
                    verified_at = (i + 1, j + 1)
                    break
                if n > 1:
                    prompt = self.model.extend_prompt(prompt, program_snippet, str(verif_result))
                time.sleep(5)
            if result:
                break
        return result, verified_at, program_snippet
