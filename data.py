"""Module to encapsulate dataset"""
import copy
import os
import json
from typing import Literal

class Data:
    """Class for data operations for schema specified in config_file"""

    def __init__(self, config_file: str = "config.json", data_root: str = "nagini_examples"):
        self.data_root = data_root
        self.config_file = config_file
        self.config = _load_json(f"{data_root}/{config_file}")
        self.verif_result: dict[str, str] = _load_json(f"{data_root}/{self.config["verif_result_cache"]}")

    def get_system_prompt(self) -> str:
        """Returns the system prompt"""
        file_name = self.config["system_prompt"]
        return _read_file(f"{self.data_root}/{file_name}")

    def get_list_of_examples(self, key: str) -> list[str]:
        """Returns the list of examples for the given key (i.e. list, bst, etc.)"""
        return list(self.config[key]["examples"].keys())

    def get_example(
        self, key: str, name: str, is_verified: Literal["unverified", "verified"]
    ) -> str:
        """Returns the example for the given key and name"""
        path = f"{self.data_root}/{self.config[key]['examples'][name][is_verified]}"
        return _read_file(path)

    def get_master_example(self, key: str, name: str) -> str | None:
        """Returns the master example for the given key and name"""
        if "master" in self.config[key]["examples"][name]:
            path = f"{self.data_root}/{self.config[key]['examples'][name]['master']}"
            return _read_file(path)
        return None

    def get_cached_result(self, key: str, example: str) -> str:
        """Returns the cached result for the unverified example"""
        return self.verif_result[example]

    def get_declaration(self, key: str) -> str:
        """Returns the declaration and predicates for the given key"""
        path = f"{self.data_root}/{self.config[key]['declaration']}"
        return _read_file(path)

    def get_dependencies(self, key: str, method_name: str) -> list[str]:
        """Returns the dependencies for the given method"""
        return self.config[key]["examples"][method_name].get("dependencies", [])

    def combine_method_with_declaration_and_dependencies(self, key: str, method_text: str, method_name: str | None = None) -> tuple[str, int]:
        """Combines the method text with the declaration file and (the transitive closure of) dependent methods and writes the output
        to a temporary file. Returns the (absolute) path to the temporary file."""
        declaration = self.get_declaration(key)
        dependencies: list[str] = []
        if method_name is not None:
            dependencies = self.config[key]["examples"][method_name].get("dependencies", [])
            dependencies = self.get_transitive_closure(key, method_name, dependencies)
        with open(f"{self.data_root}/tmp.py", "w", encoding="utf-8") as f:
            f.write(declaration + "\n")
            for program in dependencies:
                f.write(self.get_example(key, program, "verified") + "\n")
            f.write(method_text)
        num_lines = len(_read_file(f"{self.data_root}/tmp.py").split("\n"))
        # nagini expects the absolute path to the file
        return os.path.abspath(f"{self.data_root}/tmp.py"), num_lines

    def clone(self, name: str) -> "Data":
        """Clones this dataset into a new dataset with the given name"""
        data = Data()
        data.config = copy.deepcopy(self.config)
        data.verif_result = copy.deepcopy(self.verif_result)
        # Create a new directory with the given name
        os.makedirs(f"{self.data_root}/{name}", exist_ok=True)
        # Copy the config file
        os.system(f"cp {self.data_root}/{self.config_file} {self.data_root}/{name}/config.json")
        # Copy the system prompt
        os.system(f"cp {self.data_root}/{self.config["system_prompt"]} {self.data_root}/{name}")
        # Copy the declaration file
        declaration = self.config["list"]["declaration"]
        os.system(f"cp {self.data_root}/{declaration} {self.data_root}/{name}")
        # Copy the examples
        examples = self.config["list"]["examples"]
        for key in examples:
            for verified in ["unverified", "verified"]:
                example = examples[key][verified]
                os.system(f"cp {self.data_root}/{example} {self.data_root}/{name}")
        # Copy verif_result_cache
        os.system(
            f"cp {self.data_root}/{self.config['verif_result_cache']} {self.data_root}/{name}"
        )
        data.data_root = f"{self.data_root}/{name}"
        return data

    def add_example(
        self, name:str, unverified: str, verif_error: str, verified: str, key:str="list"
    ) -> None:
        """Adds an example to the dataset"""
        # write unverified and verified to file
        with open(f"{self.data_root}/{name}_unverified.txt", "w", encoding="utf-8") as f:
            f.write(unverified)
        with open(f"{self.data_root}/{name}_verified.txt", "w", encoding="utf-8") as f:
            f.write(verified)
        # add to verif_result and rewrite verif_result_cache
        self.verif_result[name] = verif_error
        with open(f"{self.data_root}/{self.config['verif_result_cache']}", "w", encoding="utf-8") as f:
            json.dump(self.verif_result, f, indent=4)
        # add to config and rewrite config.json
        self.config[key]["examples"][name] = {
            "unverified": f"{name}_unverified.txt",
            "verified": f"{name}_verified.txt",
        }
        with open(f"{self.data_root}/config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def add_example_verified_ptr(
        self, name:str, unverified: str, verif_error: str, verified_ptr: str, key:str="list"
    ) -> None:
        """Adds an example to the dataset, with verified_ptr pointing to an existing verified example"""
        # write unverified and verified to file
        with open(f"{self.data_root}/{name}_unverified.txt", "w", encoding="utf-8") as f:
            f.write(unverified)
        # add to verif_result and rewrite verif_result_cache
        self.verif_result[name] = verif_error
        with open(f"{self.data_root}/{self.config['verif_result_cache']}", "w", encoding="utf-8") as f:
            json.dump(self.verif_result, f, indent=4)
        # add to config and rewrite config.json
        self.config[key]["examples"][name] = {
            "unverified": f"{name}_unverified.txt",
            "verified": verified_ptr,
        }
        with open(f"{self.data_root}/config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)


    def add_unverified(self, name: str, unverified: str, key:str="list") -> None:
        """Adds an unverified example to the dataset"""
        unverified_file_name = self.config[key]["examples"][name]["unverified"]
        with open(f"{self.data_root}/{unverified_file_name}", "w", encoding="utf-8") as f:
            f.write(unverified)

    def add_verified(self, name: str, verified: str, key:str="list") -> None:
        """Adds a verified example to the dataset"""
        verified_file_name = self.config[key]["examples"][name]["verified"]
        with open(f"{self.data_root}/{verified_file_name}", "w", encoding="utf-8") as f:
            f.write(verified)

    def get_transitive_closure(self, key: str, method_name: str, dependencies: list[str]) -> list[str]:
        """Returns the transitive closure of the given dependencies"""
        result = []
        def dfs(node: str) -> None:
            if node not in result and node != method_name:
                result.append(node)
                for dep in self.config[key]["examples"][node].get("dependencies", []):
                    dfs(dep)
        for dep in dependencies:
            dfs(dep)
        return result

def _load_json(file_name: str) -> dict:
    with open(file_name, encoding="utf-8") as f:
        return json.load(f)


def _read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()
