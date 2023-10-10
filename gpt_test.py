"""Test GPT API"""
import os
from dotenv import load_dotenv
import openai
from nagini_client import NaginiWrapper

load_dotenv()
openai.api_key = os.getenv("GPT_SECRET_KEY")

PROMPTS_ROOT = "/home/omkar/ethz/hs23/thesis/llms-for-verified-programs/nagini_examples"
with open(os.path.join(PROMPTS_ROOT, "system_prompt")) as f:
    system_prompt = f.read()
with open(os.path.join(PROMPTS_ROOT, "prepend_unverified")) as f:
    prepend_unverified = f.read()
with open(os.path.join(PROMPTS_ROOT, "prepend_verified")) as f:
    prepend_verified = f.read()
with open(os.path.join(PROMPTS_ROOT, "traverse_unverified")) as f:
    traverse_unverified = f.read()
with open(os.path.join(PROMPTS_ROOT, "traverse_partial")) as f:
    traverse_partial = f.read()

nagini = NaginiWrapper()


def combine_method_with_declaration(declaration_file: str, method_text: str) -> str:
    """Combines the method text with the declaration file and writes the output
    to a temporary file. Returns the path to the temporary file."""
    with open(declaration_file) as f:
        declaration = f.read()
    with open(f"{PROMPTS_ROOT}/tmp.py", "w") as f:
        f.write(declaration + "\n" + method_text)
    return f"{PROMPTS_ROOT}/tmp.py"


def step(response, messages: list[dict[str, str]]) -> (str, dict[str, str]):
    """Expects: response[] to be a candidate program generated by assistant\n
    Sends the program to Nagini and appends the result to messages"""
    assert response["choices"][0]["message"]["role"] == "assistant"
    program = response["choices"][0]["message"]["content"]
    program_file = combine_method_with_declaration(f"{PROMPTS_ROOT}/list.py", program)
    result = nagini.verify(program_file)
    messages.append(
        {
            "role": "user",
            "content": f"Result from Nagini: {result}",
        }
    )
    return result, messages


LIST_DECL_PATH = f"{PROMPTS_ROOT}/list.py"

prepend_verified_verification_result = nagini.verify(
    combine_method_with_declaration(LIST_DECL_PATH, prepend_verified)
)

traverse_partial_verification_result = nagini.verify(
    combine_method_with_declaration(LIST_DECL_PATH, traverse_partial)
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": prepend_unverified},
    {
        "role": "assistant",
        "content": prepend_verified,
    },
    {
        "role": "user",
        "content": f"Result from Nagini: {prepend_verified_verification_result}",
    },
    {"role": "user", "content": traverse_unverified},
    {
        "role": "assistant",
        "content": traverse_partial,
    },
    {
        "role": "user",
        "content": f"Result from Nagini: {traverse_partial_verification_result}",
    },
]


while True:
    s = input("Press `s' to step, any other key to exit: ")
    if s == "s":
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        print(response)
        print("Generated program:\n", response["choices"][0]["message"]["content"])
        result, messages = step(response, messages)
        print("Verification result:\n", result)
    else:
        break
