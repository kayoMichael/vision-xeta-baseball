FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ./image_classification_model /app

RUN apt-get update && apt-get install -y git libglib2.0-0 libsm6 libxrender1 libxext6 && rm -rf /var/lib/apt/lists/*

RUN pip install transformers[torch] datasets pandas pillow torch torchvision torchaudio tensorboard

CMD ["python", "clip_model.py"]
