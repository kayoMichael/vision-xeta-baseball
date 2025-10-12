IMAGE_NAME = baseball-clip-train
CONTAINER_NAME = $(IMAGE_NAME)-ctr

build:
	docker build -t $(IMAGE_NAME) -f dockerfile .

train:
	docker run --rm -it \
		--name $(CONTAINER_NAME) \
		-v $(PWD):/app \
		$(IMAGE_NAME)

train-bash:
	docker run --rm -it \
		--name $(CONTAINER_NAME) \
		-v $(PWD):/app \
		$(IMAGE_NAME) bash

clean:
	docker system prune -f
