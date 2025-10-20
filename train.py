import os
import pandas as pd
import torch
from torch.utils.data import DataLoader
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

MODEL_NAME = "openai/clip-vit-base-patch16"


class LossTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        """
        Override compute_loss from Trainer to return the loss for backpropagation
        """
        outputs = model(**inputs, return_loss=True)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss

class TrainCLIP:
    def __init__(self):
        self.model = CLIPModel.from_pretrained(MODEL_NAME)
        self.processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        self.root = "data_set"
        self.dataset = None

    def _data_set_setup(self):
        data = []
        for path, _, files in os.walk(self.root):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    rel_path = os.path.relpath(path, self.root)
                    label = "bowman " + rel_path.replace(os.sep, " ") + " baseball card"
                    data.append({"image": os.path.join(path, f), "label": label})
        df = pd.DataFrame(data)
        df.to_csv("cards.csv", index=False)
        print(f"Saved {len(df)} samples with {df['label'].nunique()} unique labels.")

        features = Features({"image": Image(), "label": Value("string")})
        self.dataset = load_dataset("csv", data_files="cards.csv", features=features)["train"]

    def _preprocess(self, data):
        process = self.processor(
            text=data["label"],
            images=data["image"],
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        return {
            "input_ids": process["input_ids"][0],
            "attention_mask": process["attention_mask"][0],
            "pixel_values": process["pixel_values"][0]
        }

    def train_model(self):
        self._data_set_setup()

        split = self.dataset.train_test_split(test_size=0.2, seed=42)
        train_ds = split["train"]
        val_ds = split["test"]

        def collate_fn(batch):
            images = [item["image"] for item in batch]
            texts = [item["label"] for item in batch]

            proc = self.processor(
                text=texts,
                images=images,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            return proc

        training_args = TrainingArguments(
            output_dir="./clip-card-model",
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            num_train_epochs=15,
            learning_rate=5e-6,
            fp16=True,
            remove_unused_columns=False,
            save_strategy="epoch",
            eval_strategy="epoch",
            load_best_model_at_end=False,
            logging_steps=50,
            logging_dir="./logs",
        )
        trainer = LossTrainer(
            model=self.model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=val_ds,
            data_collator=collate_fn,
        )
        trainer.train()
        trainer.save_model("./clip-card-model")
        self.processor.save_pretrained("./clip-card-model")


    def compute_retrieval_accuracy(self, batch_size=64):
        """
        Compute class-level retrieval accuracy (Image -> Text) on the validation split.
        """
        self._data_set_setup()
        split = self.dataset.train_test_split(test_size=0.2, seed=42)
        val_ds = split["test"]

        self.model.eval()

        img_embs = []
        txt_embs = []
        labels = []

        def collate_fn(batch):
            images = [item["image"] for item in batch]
            texts = [item["label"] for item in batch]

            proc = self.processor(
                text=texts,
                images=images,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            return proc, texts

        dataloader = DataLoader(
            val_ds,
            batch_size=batch_size,
            collate_fn=lambda b: collate_fn(b),
            shuffle=False
        )

        with torch.no_grad():
            for proc, batch_labels in dataloader:
                pixel_values = proc["pixel_values"].to(device)
                input_ids = proc["input_ids"].to(device)
                attention_mask = proc["attention_mask"].to(device)

                img_feat = self.model.get_image_features(pixel_values)
                txt_feat = self.model.get_text_features(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                img_feat = img_feat / img_feat.norm(dim=-1, keepdim=True)
                txt_feat = txt_feat / txt_feat.norm(dim=-1, keepdim=True)

                img_embs.append(img_feat.cpu())
                txt_embs.append(txt_feat.cpu())
                labels.extend(batch_labels)

        img_embs = torch.cat(img_embs, dim=0)
        txt_embs = torch.cat(txt_embs, dim=0)

        sims = img_embs @ txt_embs.T

        # Correct prediction
        preds = sims.argmax(dim=1)
        top1_correct = sum(labels[i] == labels[preds[i]] for i in range(len(labels)))
        top1_acc = top1_correct / len(labels)

        # Top 5 Accuracy
        top5 = sims.topk(5, dim=1).indices
        top5_correct = sum(any(labels[p] == labels[i] for p in top5[i])
                           for i in range(len(labels)))
        top5_acc = top5_correct / len(labels)

        print(f"Validation samples: {len(labels)}")
        print(f"Class-level Top-1 Accuracy: {top1_acc:.4f}")
        print(f"Class-level Top-5 Accuracy: {top5_acc:.4f}")

        return top1_acc, top5_acc
