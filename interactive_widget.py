"""A widget to interact with (add examples, verify, etc.) the model."""
import dataclasses
import random
import ipywidgets as widgets  # type: ignore[import]
import evaluation


@dataclasses.dataclass
class State:
    """State for the interactive widget"""

    is_unverified: bool = True
    example_count: int = 0
    unverified_program: str = ""
    verified_program: str = ""
    verif_error: str = ""
    program_gpt: str = ""
    verif_result_gpt: str = ""


class PromptAndVerifyWidget:
    """A widget to interact with (add examples, verify, etc.) the model."""

    def __init__(self, ev: evaluation.Evaluation, example:str, key="list") -> None:
        self.ev = ev
        self.example = example
        self.key = key
        self.state = State()
        self.out = widgets.Output()
        self.w = widgets.Textarea("Enter unverified program", rows=10)
        self.v = widgets.Textarea("", description="VerificationResult", disabled=True)
        self.verify_button = widgets.Button(description="Verify")
        self.confirm_button = widgets.Button(description="Confirm")
        self.extend_button = widgets.Button(description="Extend")

        self.out.layout.height = "300px"
        self.out.layout.width = "100%"
        self.out.layout.overflow = "scroll"
        self.w.layout.width = "100%"
        self.v.layout.width = "100%"
        self.verify_button.on_click(self.verify_callback)
        self.confirm_button.on_click(self.confirm_callback)
        self.extend_button.on_click(self.extend_callback)

        self.widget = widgets.VBox(
            [
                self.out,
                self.extend_button,
                self.w,
                self.verify_button,
                self.v,
                self.confirm_button,
            ]
        )
        self.prompt = None
        self.n = 0  # the error depth

        self.seed = random.Random(42).randint(12345, 54321)

    def extend_callback(self, *args):
        """Extend the prompt with the program snippet and verification result."""
        self._extend_interactive()

    def verify_callback(self, *args):
        """Verify the program snippet in the text area."""
        program_snippet = self.w.value
        verif_result = self.ev.verify_program_snippet("list", program_snippet)
        self.v.value = str(verif_result)

    def confirm_callback(self, *args):
        """Confirm the program snippet in the text area."""
        self.out.append_stdout(
            f"Confirming...{'unverified' if self.state.is_unverified else 'verified'}\n"
        )
        if self.state.is_unverified:
            self.state.unverified_program = self.w.value
            self.state.verif_error = self.v.value
            self.state.is_unverified = False
            self.w.value = "Enter verified program"
        else:
            self.state.example_count += 1
            self.state.verified_program = self.w.value
            self.ev.data.add_example(
                f"example_{self.state.example_count}",
                self.state.unverified_program,
                self.state.verif_error,
                self.state.verified_program,
            )
            self.out.append_stdout(
                f"Added example_{self.state.example_count} to the dataset\n"
            )
            self.state.is_unverified = True
            self.w.value = "Enter unverified program"
            self.n = 0
            self.run_interactive()

    def show(self):
        """Show the widget."""
        self.widget.layout.display = "initial"

    def hide(self):
        """Hide the widget."""
        self.widget.layout.display = "none"

    def run_interactive(self) -> None:
        """Starts an interactive session for the given example"""
        self.n += 1
        self.out.clear_output()
        self.out.append_stdout(f"Running example: {self.example}; error depth: {self.n}\n")
        self.prompt = self.ev.model.get_prompt(self.example, self.key)
        self._get_response_and_update_state()

    def _get_response_and_update_state(self) -> None:
        response = self.ev.model.get_response(self.prompt, seed=self.seed)
        program_snippet = self.ev.model.print_and_process_response(response)
        verif_result = self.ev.verify_program_snippet(self.key, program_snippet)
        with self.out:
            print(program_snippet)
            print(str(verif_result))
        self.state.program_gpt = program_snippet
        self.state.verif_result_gpt = str(verif_result)

    def _extend_interactive(self):
        self.ev.model.extend_prompt(
            self.prompt, self.state.program_gpt, self.state.verif_result_gpt
        )
        self.n += 1
        with self.out:
            print("\n=====================================\n")
            print(f"Running example: {self.example}; error depth: {self.n}")
        self._get_response_and_update_state()


# display(widgets.HBox([out]), w, verify_button, v, confirm_button)
