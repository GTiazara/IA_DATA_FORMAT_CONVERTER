VERSION ?= 0.1.0
NAME := ia-data-format-converter
SIF_NAME := $(NAME)-$(VERSION).sif
DOCKER_NAME := $(NAME):$(VERSION)
DOCKER_TAR := $(NAME)-$(VERSION).tar
DEF_FILE := $(NAME).def

APPTAINER_BIND := \
	--bind ./input:/app/input \
	--bind ./output:/app/output

.PHONY: build build-docker docker-tar build-sif clean shell help \
	run-shell run-exec-csv-to-feather run-exec-feather-to-csv

help:
	@echo "Targets:"
	@echo "  build                    Build Docker image, export tar, then SIF file"
	@echo "  build-docker             Build Docker image only"
	@echo "  docker-tar               Export Docker image to a tar archive"
	@echo "  build-sif                Build SIF from the exported tar (no Docker socket needed)"
	@echo "  shell                    Open a shell in the Docker image"
	@echo "  run-shell                Open an Apptainer shell in the SIF"
	@echo "  run-exec-csv-to-feather  Convert CSV -> Feather inside the SIF"
	@echo "  run-exec-feather-to-csv  Convert Feather -> CSV inside the SIF"
	@echo "  clean                    Remove generated SIF and tar files"
	@echo ""
	@echo "Variables:"
	@echo "  VERSION=$(VERSION)"
	@echo "  SIF_NAME=$(SIF_NAME)"
	@echo "  DOCKER_NAME=$(DOCKER_NAME)"
	@echo "  DOCKER_TAR=$(DOCKER_TAR)"

build: build-docker build-sif

build-docker:
	docker build -t $(DOCKER_NAME) .

docker-tar: build-docker
	docker save $(DOCKER_NAME) -o $(DOCKER_TAR)

build-sif: docker-tar
	rm -f $(SIF_NAME)
	apptainer build \
		--build-arg TAR_FILE=$(DOCKER_TAR) \
		--build-arg VERSION=$(VERSION) \
		$(SIF_NAME) $(DEF_FILE)

shell:
	docker run --rm -it $(DOCKER_NAME) bash

clean:
	rm -f $(SIF_NAME) $(DOCKER_TAR)

run-shell:
	apptainer shell \
		$(APPTAINER_BIND) \
		$(SIF_NAME)

run-exec-csv-to-feather:
	apptainer exec --pwd /app \
		$(APPTAINER_BIND) \
		--bind ./config_csv_to_feather_example.yaml:/app/config_csv_to_feather_example.yaml \
		$(SIF_NAME) \
		csv-feather-convert config_csv_to_feather_example.yaml

run-exec-feather-to-csv:
	apptainer exec --pwd /app \
		$(APPTAINER_BIND) \
		--bind ./config_feather_to_csv_example.yaml:/app/config_feather_to_csv_example.yaml \
		$(SIF_NAME) \
		csv-feather-convert config_feather_to_csv_example.yaml
