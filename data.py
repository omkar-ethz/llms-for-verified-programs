"""Module to encapsulate dataset"""
import json
from typing import Literal

DATA_ROOT = "nagini_examples"


class Data:
    """Data provider according to config.json"""

    def __init__(self) -> None:
        self.config = _load_config()

    def get_system_prompt(self) -> str:
        """Returns the system prompt"""
        path = f"{DATA_ROOT}/{self.config['system_prompt']}"
        return _read_file(path)

    def get_list_of_examples(self, key) -> list[str]:
        """Returns the list of examples for the given key (i.e. list, bst, etc.)"""
        return list(self.config[key]["examples"].keys())

    def get_example(
        self, key: str, name: str, is_verified: Literal["unverified", "verified"]
    ) -> str:
        """Returns the example for the given key and name"""
        path = f"{DATA_ROOT}/{self.config[key]['examples'][name][is_verified]}"
        return _read_file(path)

    def get_declaration(self, key: str) -> str:
        """Returns the declaration and predicates for the given key"""
        path = f"{DATA_ROOT}/{self.config[key]['declaration']}"
        return _read_file(path)

    def get_config(self) -> dict:
        """Returns the config dict"""
        return self.config


def _read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _load_config() -> dict:
    with open("nagini_examples/config.json", encoding="utf-8") as f:
        return json.load(f)


# some test code
# c: Data = Data()
# print(c.get_list_of_examples("list"))
# conf_dict = c.get_config()
# print(conf_dict)
# print(c.get_declaration("list"))
# print(c.get_example("list", "prepend", "verified"))
# print(c.get_example("list", "prepend", "unverified"))
