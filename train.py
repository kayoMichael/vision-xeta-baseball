import os

import pandas as pd
import torch
from datasets import load_dataset, Features, Value, Image
from transformers import (
    CLIPProcessor,
    CLIPModel,
    Trainer,
    TrainingArguments,
)

if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

MODEL_NAME = "openai/clip-vit-base-patch32"

root = "data_set"
data = []
for path, _, files in os.walk(root):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            rel_path = os.path.relpath(path, root)
            label = "bowman " + rel_path.replace(os.sep, " ") + " baseball card"
            data.append({"image": os.path.join(path, f), "label": label})
df = pd.DataFrame(data)
df.to_csv("cards.csv", index=False)
print(f"Saved {len(df)} samples with {df['label'].nunique()} unique labels.")

features = Features({"image": Image(), "label": Value("string")})
dataset = load_dataset("csv", data_files="cards.csv", features=features)["train"]


processor = CLIPProcessor.from_pretrained(MODEL_NAME)
model = CLIPModel.from_pretrained(MODEL_NAME)

for param in model.text_model.parameters():
    param.requires_grad = False

def preprocess(data):
    return processor(
        text=data["label"],
        images=data["image"],
        return_tensors="pt",
        padding=True,
        truncation=True
    )
processed = dataset.map(preprocess, remove_columns=dataset.column_names)

def compute_loss(model, inputs, return_outputs=False):
    pixel_values = torch.stack(inputs["pixel_values"]).squeeze(1).to(model.device)
    input_ids = torch.stack(inputs["input_ids"]).squeeze(1).to(model.device)
    attention_mask = torch.stack(inputs["attention_mask"]).squeeze(1).to(model.device)
    outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        pixel_values=pixel_values,
        return_loss=True
    )
    loss = outputs.loss
    return (loss, outputs) if return_outputs else loss

training_args = TrainingArguments(
    output_dir="./clip-card-model",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    learning_rate=5e-6,
    fp16=True,
    remove_unused_columns=False,
    save_strategy="epoch",
    logging_steps=50,
    logging_dir="./logs",
    report_to="tensorboard",
)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=processed,
    compute_loss_func=compute_loss,
)
trainer.train()
trainer.save_model("./clip-card-model")
processor.save_pretrained("./clip-card-model")