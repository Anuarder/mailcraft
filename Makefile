.PHONY: up down send send-all list build new

lang ?= en

up:
	@docker compose up -d
	@echo ""
	@echo "=========================================="
	@echo "  Mailcraft — Email Template Sandbox"
	@echo "=========================================="
	@echo ""
	@echo "  Mailpit UI:  http://localhost:8025"
	@echo "  SMTP Port:   1025"
	@echo ""
	@echo "  Usage:"
	@echo "    make send t=<template>    Send a single template (lang=$(lang))"
	@echo "    make send-all             Send all templates (lang=$(lang))"
	@echo "    make list                 List available templates"
	@echo "    make new t=<name>         Scaffold a new template"
	@echo "    make down                 Stop services"
	@echo ""
	@echo "  Examples:"
	@echo "    make send t=welcome"
	@echo "    make send t=password_reset lang=ru"
	@echo "    make send-all lang=ru"
	@echo "    make new t=order_confirmation"
	@echo ""
	@echo "=========================================="
	@echo ""

down:
	docker compose down

build:
	docker compose build

send:
	@docker compose run --rm app python send.py send $(t) --lang $(lang)

send-all:
	@docker compose run --rm app python send.py send-all --lang $(lang)

list:
	@docker compose run --rm app python send.py list

new:
	@mkdir -p templates/$(t)
	@echo '{% extends "base.html" %}' > templates/$(t)/email.html
	@echo '' >> templates/$(t)/email.html
	@echo '{% block title %}{{ page_title }}{% endblock %}' >> templates/$(t)/email.html
	@echo '' >> templates/$(t)/email.html
	@echo '{% block content %}' >> templates/$(t)/email.html
	@echo '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">' >> templates/$(t)/email.html
	@echo '  <tr>' >> templates/$(t)/email.html
	@echo '    <td align="center" style="font-family: Arial, Helvetica, sans-serif; font-size: 22px; font-weight: 700; line-height: 1.2; color: #333333; padding-bottom: 16px;">' >> templates/$(t)/email.html
	@echo '      {{ heading }}' >> templates/$(t)/email.html
	@echo '    </td>' >> templates/$(t)/email.html
	@echo '  </tr>' >> templates/$(t)/email.html
	@echo '  <tr>' >> templates/$(t)/email.html
	@echo '    <td align="center" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 1.5; color: #666666; padding-bottom: 24px;">' >> templates/$(t)/email.html
	@echo '      {{ body_text }}' >> templates/$(t)/email.html
	@echo '    </td>' >> templates/$(t)/email.html
	@echo '  </tr>' >> templates/$(t)/email.html
	@echo '</table>' >> templates/$(t)/email.html
	@echo '{% endblock %}' >> templates/$(t)/email.html
	@echo '{}' > templates/$(t)/data.json
	@echo ""
	@echo "Created template: templates/$(t)/"
	@echo "  - templates/$(t)/email.html"
	@echo "  - templates/$(t)/data.json"
	@echo ""
	@echo "Edit these files and run: make send t=$(t)"
