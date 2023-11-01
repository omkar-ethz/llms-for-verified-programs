"""Utility function for miscellaneous tasks"""
import pickle
import data
import evaluation


def print_and_process_response(response: dict) -> str:
    """Print response from GPT and return the program snippet"""
    program_snippet = response["choices"][0]["message"]["content"]
    print("Generated program from GPT:")
    print(program_snippet)
    print("=====================================")
    return program_snippet


def cache_nagini_results() -> None:
    """Run nagini on all unverified programs in the dataset and store pickled results"""
    examples = data.get_list_of_examples("list")
    verif_result: dict[str, str] = {}
    for example in examples:
        program_snippet = data.get_example("list", example, "unverified")
        result = evaluation._verify_program_snippet("list", program_snippet)
        verif_result[example] = str(result)
    print(verif_result)
    with open(f"{data.DATA_ROOT}/verif_result.pkl", "wb") as f:
        pickle.dump(verif_result, f)
