"""Contains functions to get various prompt combinations"""
import os
from data import Data, DATA_ROOT
from nagini_client import NaginiWrapper

data = Data()
config = data.get_config()

nagini = NaginiWrapper()


def get_few_shot_prompt(hold_out: str, key: str = "list") -> list[dict[str, str]]:
    """Returns a prompt with the solution to hold_out example held out"""
    examples = data.get_list_of_examples(key)
    messages = [{"role": "system", "content": data.get_system_prompt()}]
    for example in examples:
        if example is not hold_out:
            messages.append(
                {
                    "role": "user",
                    "content": data.get_example(key, example, "unverified"),
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": data.get_example(key, example, "verified"),
                }
            )
    messages.append(
        {"role": "user", "content": data.get_example(key, hold_out, "unverified")}
    )
    return messages


def run_single(key: str, program_snippet:str) -> str:
    """Expects: response contains a candidate program generated by assistant\n
    Sends the program to Nagini and returns the verification result"""
    program_file = _combine_method_with_declaration(key, program_snippet)
    return nagini.verify(program_file)


def _combine_method_with_declaration(key: str, method_text: str) -> str:
    """Combines the method text with the declaration file and writes the output
    to a temporary file. Returns the (absolute) path to the temporary file."""
    declaration = data.get_declaration(key)
    with open(f"{DATA_ROOT}/tmp.py", "w", encoding="utf-8") as f:
        f.write(declaration + "\n" + method_text)
    # nagini expects the absolute path to the file
    return os.path.abspath(f"{DATA_ROOT}/tmp.py")


# print(get_few_shot_prompt("prepend"))
# print(run_single("list", data.get_example("list", "join_lists", "unverified")))
