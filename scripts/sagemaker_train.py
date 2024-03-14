import os
import torch
from peft import LoraConfig, PeftModel
from trl import SFTTrainer # type: ignore
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, LlamaForCausalLM, CodeLlamaTokenizer  # type: ignore
from datasets import load_from_disk  # type: ignore


output_data_dir = "/opt/ml/checkpoints"
model_dir = os.environ["SM_MODEL_DIR"]
training_dir = os.environ["SM_CHANNEL_TRAIN"]
testing_dir = os.environ["SM_CHANNEL_TEST"]

train_dataset = load_from_disk(training_dir)
eval_dataset = load_from_disk(testing_dir)

BASE_MODEL = "codellama/CodeLlama-7b-hf"
model: LlamaForCausalLM = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    load_in_8bit=True,
    torch_dtype=torch.float16,
    device_map="auto",
)
tokenizer: CodeLlamaTokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token_id = 0
tokenizer.padding_side = "left"
tokenizer.add_eos_token = True

# def tokenize(prompt):
#     result = tokenizer(
#         prompt,
#         max_length=1024,
#         padding="max_length",
#         return_tensors=None,
#     )

#     # "self-supervised learning" means the labels are also the inputs:
#     result["labels"] = result["input_ids"].copy()

#     return result

# def generate_and_tokenize_prompt(data_point):
#     return tokenize(data_point["prompt"])

# tokenized_train_dataset = train_dataset.map(generate_and_tokenize_prompt)
# tokenized_val_dataset = eval_dataset.map(generate_and_tokenize_prompt)

peft_config = LoraConfig(
    r=64,  # the rank of the LoRA matrices
    lora_alpha=64,  # to match the paper
    lora_dropout=0.1,  # dropout to add to the LoRA layers
    bias="none",  # add bias to the nn.Linear layers?
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],  # the name of the layers to add LoRA
    modules_to_save=None,  # layers to unfreeze and train from the original pre-trained model
)
# model.train()  # put model back into training mode
# model = prepare_model_for_int8_training(model)
# model = get_peft_model(model, peft_config)
# model.print_trainable_parameters()

training_arguments = TrainingArguments(
    output_dir=output_data_dir,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    num_train_epochs=4,
    optim="adamw_torch",
    save_strategy="epoch",
    evaluation_strategy="epoch",
    learning_rate=2e-4,
    max_grad_norm=0.3,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    gradient_checkpointing=True,
    load_best_model_at_end=False,
    bf16=True,
)


# trainer = Trainer(
#     model=model,
#     train_dataset=tokenized_train_dataset,
#     eval_dataset=tokenized_val_dataset,
#     args=training_arguments,
# )

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    dataset_text_field="prompt",
    args=training_arguments,
    peft_config=peft_config,
    max_seq_length=1024,
)

trainer.train()

trainer.save_model(model_dir)
