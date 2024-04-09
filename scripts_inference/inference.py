from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
from peft import PeftModel, LoraModel
import torch


def model_fn(model_dir):
    # Load model from HuggingFace Hub
    base_model = "codellama/CodeLlama-7b-hf"
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        load_in_8bit=True,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model: LoraModel = PeftModel.from_pretrained(model, model_dir)
    model = model.merge_and_unload()
    model.eval()
    print("Model loaded on: ", model.device)
    return model, tokenizer


def predict_fn(data, model_and_tokenizer):
    model, tokenizer = model_and_tokenizer
    sentences = data.pop("inputs", data)
    generate_params = data.pop("params", {})
    decode_params = data.pop("decode_params", {})
    encoded_input = tokenizer(sentences, return_tensors="pt").to(model.device)
    prompt_length = encoded_input["input_ids"].shape[1]
    output = model.generate(**encoded_input, **generate_params)[0][prompt_length:]
    with torch.no_grad():
        return tokenizer.decode(output, **decode_params)
