"""Module to encapsulate dataset"""
import os
import json
import pickle
from typing import Literal

DATA_ROOT = "nagini_examples"


class Data:
    """Class for data operations for schema specified in config_file"""

    def __init__(self, config_file: str = "config.json"):
        self.config = _load_config(config_file)
        self.verif_result = _load_cached_nagini_results(
            self.config["verif_result_cache"]
        )

    def get_system_prompt(self) -> str:
        """Returns the system prompt"""
        file_name = self.config["system_prompt"]
        return _read_file(f"{DATA_ROOT}/{file_name}")

    def get_list_of_examples(self, key) -> list[str]:
        """Returns the list of examples for the given key (i.e. list, bst, etc.)"""
        return list(self.config[key]["examples"].keys())

    def get_example(
        self, key: str, name: str, is_verified: Literal["unverified", "verified"]
    ) -> str:
        """Returns the example for the given key and name"""
        path = f"{DATA_ROOT}/{self.config[key]['examples'][name][is_verified]}"
        return _read_file(path)

    def get_cached_result(self, key: str, example: str) -> str:
        """Returns the cached result for the unverified example"""
        return self.verif_result[example]

    def get_declaration(self, key: str) -> str:
        """Returns the declaration and predicates for the given key"""
        path = f"{DATA_ROOT}/{self.config[key]['declaration']}"
        return _read_file(path)

    def combine_method_with_declaration(self, key: str, method_text: str) -> str:
        """Combines the method text with the declaration file and writes the output
        to a temporary file. Returns the (absolute) path to the temporary file."""
        declaration = self.get_declaration(key)
        with open(f"{DATA_ROOT}/tmp.py", "w", encoding="utf-8") as f:
            f.write(declaration + "\n" + method_text)
        # nagini expects the absolute path to the file
        return os.path.abspath(f"{DATA_ROOT}/tmp.py")


def _load_config(file_name: str) -> dict:
    with open(f"{DATA_ROOT}/{file_name}", encoding="utf-8") as f:
        return json.load(f)


def _load_cached_nagini_results(file_name: str) -> dict:
    with open(f"{DATA_ROOT}/{file_name}", "rb") as f:
        verif_result = pickle.load(f)
    return verif_result


def _read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()
