"""Test GPT API"""
import os
from dotenv import load_dotenv
import openai
from nagini_client import NaginiWrapper

load_dotenv()
openai.api_key = os.getenv("GPT_SECRET_KEY")

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {
            "role": "assistant",
            "content": "The Los Angeles Dodgers won the World Series in 2020.",
        },
        {"role": "user", "content": "Where was it played?"},
    ],
)

print(response)
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

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prepend_unverified},
        {
            "role": "assistant",
            "content": prepend_verified,
        },
        {
            "role": "user",
            "content": f"Result from Nagini: {nagini.verify(PROMPTS_ROOT + '/prepend_verified')}",
        },
        {"role": "user", "content": traverse_unverified},
        {
            "role": "assistant",
            "content": traverse_partial,
        },
        {
            "role": "user",
            "content": f"Result from Nagini: {nagini.verify(PROMPTS_ROOT + '/traverse_partial')}",
        },
    ],
)

print(response)