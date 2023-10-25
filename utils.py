"""Utility function for miscellaneous tasks"""

def print_and_process_response(response:dict) -> str:
    """Print response from GPT and return the program snippet"""
    program_snippet = response["choices"][0]["message"]["content"]
    print("Generated program from GPT:")
    print(program_snippet)
    print("=====================================")
    return program_snippet