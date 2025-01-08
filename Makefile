.PHONY: auth start stop restart clean logs help build up down env-edit rebuild-app

# Переменные
DC = docker compose
NAME = $(shell grep NAME .env | cut -d '=' -f2)
SESSION_FILE = src/$(NAME).session

help:
	@echo "Доступные команды:"
	@echo "  make build     - Сборка образов"
	@echo "  make up        - Создание и запуск контейнеров"
	@echo "  make down      - Остановка и удаление контейнеров"
	@echo "  make auth      - Запуск только аутентификации"
	@echo "  make start     - Запуск существующих контейнеров"
	@echo "  make stop      - Приостановка контейнеров"
	@echo "  make restart   - Перезапуск контейнеров"
	@echo "  make rebuild   - Пересборка и перезапуск контейнеров"
	@echo "  make clean     - Очистка контейнеров и volumes"
	@echo "  make logs      - Просмотр логов"

build:
	@echo "Сборка образов..."
	@$(DC) build

up:
	@echo "Создание и запуск контейнеров..."
	@$(DC) up -d

down:
	@echo "Остановка и удаление контейнеров..."
	@$(DC) down

auth:
	@echo "Запуск процесса аутентификации..."
	@$(DC) run --rm auth

start:
	@if [ ! -f $(SESSION_FILE) ]; then \
		echo "Файл сессии не найден. Запуск аутентификации..."; \
		$(DC) run --rm auth; \
	fi
	@if [ -f $(SESSION_FILE) ]; then \
		echo "Запуск сервисов..."; \
		$(DC) start redis app; \
		echo "Сервисы запущены!"; \
	else \
		echo "Ошибка: Файл сессии не создан. Проверьте процесс аутентификации."; \
		exit 1; \
	fi

stop:
	@echo "Приостановка сервисов..."
	@$(DC) stop

restart:
	@echo "Перезапуск сервисов..."
	@$(DC) restart

rebuild: down build up
	@echo "Пересборка завершена"

clean:
	@echo "Очистка контейнеров и volumes..."
	@$(DC) down -v
	@rm -f $(SESSION_FILE)
	@echo "Очистка завершена"

logs:
	@$(DC) logs -f

rebuild-app:
	@echo "Пересборка приложения..."
	@$(DC) down app auth
	@$(DC) build app auth
	@echo "Запуск аутентификации..."
	@$(DC) run --rm auth
	@$(DC) up -d app
	@echo "Пересборка завершена"