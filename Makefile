PI_IP_ADDRESS=10.0.0.36
PI_USERNAME=pi

.PHONY: run
run:
	@docker compose up -d

.PHONY: install
install:
	@cd scripts && bash install.sh

.PHONY: copy
copy:
	@rsync -a $(shell pwd) --exclude env $(PI_USERNAME)@$(PI_IP_ADDRESS):/home/$(PI_USERNAME)

.PHONY: shell
shell:
	@ssh $(PI_USERNAME)@$(PI_IP_ADDRESS)

.PHONY: build
build:
	@docker compose build

.PHONY: rebuild
rebuild:
	@docker stop pi_air_quality_monitor-web-1 && docker stop pi_air_quality_monitor-redis-1 && docker compose build && docker compose up -d
