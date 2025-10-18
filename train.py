import os

import pandas as pd
import torch
from datasets import load_dataset, Features, Value, Image
from transformers import (
    CLIPProcessor,
    CLIPModel,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
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
        :param model:
        :param inputs:
        :param return_outputs:
        :param kwargs:
        :return:
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
        self.processed = None

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

    def _tokenize_process(self):
        for param in self.model.text_model.parameters():
            param.requires_grad = False
        self.processed = self.dataset.map(self._preprocess, remove_columns=self.dataset.column_names)

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
        self._tokenize_process()
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
        data_collator = DataCollatorWithPadding(tokenizer=self.processor.tokenizer)
        trainer = LossTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.processed,
            data_collator=data_collator,
        )
        trainer.train()
        trainer.save_model("./clip-card-model")
        self.processor.save_pretrained("./clip-card-model")

    def compute_retrieval_accuracy(self):
        self.model.eval()
        img_embs = []
        txt_embs = []

        with torch.no_grad():
            for sample in self.processed:
                pixel = torch.tensor(sample["pixel_values"]).unsqueeze(0).to(self.model.device)
                txt_in = {
                    "input_ids": torch.tensor(sample["input_ids"]).unsqueeze(0).to(self.model.device),
                    "attention_mask": torch.tensor(sample["attention_mask"]).unsqueeze(0).to(self.model.device)
                }

                img_emb = self.model.get_image_features(pixel)
                txt_emb = self.model.get_text_features(**txt_in)

                img_emb = img_emb / img_emb.norm(dim=-1, keepdim=True)
                txt_emb = txt_emb / txt_emb.norm(dim=-1, keepdim=True)

                img_embs.append(img_emb.squeeze(0))
                txt_embs.append(txt_emb.squeeze(0))

        img_embs = torch.stack(img_embs)
        txt_embs = torch.stack(txt_embs)

        sims = img_embs @ txt_embs.T

        correct = (sims.argmax(dim=1) == torch.arange(len(self.processed), device=sims.device)).sum().item()
        acc = correct / len(self.processed)
        return acc


if __name__ == "__main__":
    clip = TrainCLIP()
    clip.train_model()
    print(clip.compute_retrieval_accuracy())
