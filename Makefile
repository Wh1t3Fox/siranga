export DOCKER_BUILDKIT=1

APP_NAME := siranga

ifndef SUDO_USER
SSH_CONFIG := $(HOME)/.ssh/
else
SSH_CONFIG := /home/$(SUDO_USER)/.ssh/
endif

GIT_NOT_CLEAN_CHECK = $(shell git status --porcelain)

ifeq ($(MAKECMDGOALS),release)

ifneq (x$(GIT_NOT_CLEAN_CHECK), x)
$(error echo You are trying to release a build based on a dirty repo)
endif

endif

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build:	## Build Docker Container for Testing
	@docker build . -t siranga

test: build	## Launch siranga in Docker Container
	docker run -it --rm --net host -v "$(SSH_CONFIG):/home/user/.ssh/" $(APP_NAME)

release:	## Publish version to pypi
	python setup.py sdist
	twine upload dist/*

clean:	## Cleanup all files
	@docker rmi siranga 2>/dev/null || true
	@rm -fr dist siranga.egg-info || true

.PHONY: help build-img run release clean
.DEFAULT_GOAL := help
