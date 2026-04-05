.PHONY: up down build logs ps clean

COMPOSE := docker-compose -f docker-compose.dev.yml

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f app

ps:
	$(COMPOSE) ps

clean:
	$(COMPOSE) down -v
