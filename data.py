"""Module to encapsulate dataset"""
import json
import pickle
from typing import Literal

DATA_ROOT = "nagini_examples"


def _load_config() -> dict:
    with open(f"{DATA_ROOT}/config.json", encoding="utf-8") as f:
        return json.load(f)


def _load_cached_nagini_results() -> dict:
    with open(f"{DATA_ROOT}/verif_result.pkl", "rb") as f:
        verif_result = pickle.load(f)
    return verif_result


def _read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


_config = _load_config()
_verif_result = _load_cached_nagini_results()


def get_system_prompt(file_name=_config["system_prompt"]) -> str:
    """Returns the system prompt"""
    return _read_file(f"{DATA_ROOT}/{file_name}")


def get_list_of_examples(key) -> list[str]:
    """Returns the list of examples for the given key (i.e. list, bst, etc.)"""
    return list(_config[key]["examples"].keys())


def get_example(
    key: str, name: str, is_verified: Literal["unverified", "verified"]
) -> str:
    """Returns the example for the given key and name"""
    path = f"{DATA_ROOT}/{_config[key]['examples'][name][is_verified]}"
    return _read_file(path)


def get_cached_result(key: str, example: str) -> str:
    """Returns the cached result for the unverified example"""
    return _verif_result[example]


def get_declaration(key: str) -> str:
    """Returns the declaration and predicates for the given key"""
    path = f"{DATA_ROOT}/{_config[key]['declaration']}"
    return _read_file(path)
