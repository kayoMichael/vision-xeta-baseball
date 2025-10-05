import os, pandas as pd
from transformers import CLIPProcessor, CLIPModel, Trainer, TrainingArguments
from datasets import load_dataset, Features, Value, Image

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
dataset = load_dataset("csv", data_files="cards.csv", features=features)

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

def preprocess(example):
    return processor(
        text=example["label"],
        images=example["image"],
        padding=True
    )

processed = dataset["train"].map(
    preprocess,
    batched=True,
    batch_size=8,
    remove_columns=dataset["train"].column_names
)

training_args = TrainingArguments(
    output_dir="./clip-card-model",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    learning_rate=5e-6,
    fp16=True,
    remove_unused_columns=False,
    save_strategy="epoch",
    logging_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=processed,
)

trainer.train()
