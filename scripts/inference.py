from transformers import AutoTokenizer, AutoModelForCausalLM # type: ignore
from peft import PeftModel
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
    model = PeftModel.from_pretrained(model, model_dir)
    return model, tokenizer

def predict_fn(data, model_and_tokenizer):
    # destruct model and tokenizer
    model, tokenizer = model_and_tokenizer
    
    # Tokenize sentences
    sentences = data.pop("inputs", data)
    generate_params = data.pop("params", {})
    decode_params = data.pop("decode_params", {})
    encoded_input = tokenizer(sentences, return_tensors='pt').to(model.device)

    # Compute token embeddings
    with torch.no_grad():
        return tokenizer.decode(model.generate(**encoded_input, **generate_params)[0], **decode_params)

