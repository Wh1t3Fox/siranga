export DOCKER_BUILDKIT=1

ifndef SUDO_USER
	SSH_CONFIG = $(HOME)/.ssh/
else
	SSH_CONFIG = /home/$(SUDO_USER)/.ssh/
endif

default: run

build-img:
	@docker build . -t siranga

run: build-img
	docker run -it --rm --net host -v "$(SSH_CONFIG):/home/user/.ssh/" siranga


.PHONY: build-img run
