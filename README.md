# Mailcraft

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-required-blue?logo=docker)](https://docs.docker.com/get-docker/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Anuarder/mailcraft/pulls)

Local email template development sandbox. Build, preview, and test HTML email templates without any external services.

**Clone. Start. Send. See your emails instantly.**

## Why

Building HTML emails is painful. Email clients have quirky rendering engines, and you can't just "open in browser" — you need to see how your email actually looks when received. Mailcraft gives you:

- Instant local preview via [Mailpit](https://mailpit.axe.dev/) — a fake SMTP server with a web UI
- Jinja2 templating with base layouts, variables, and i18n support
- Zero dependencies beyond Docker — no Python, no Node.js needed on your machine
- Simple `make` commands to send, preview, and scaffold templates

## Quick Start

```bash
git clone https://github.com/Anuarder/mailcraft.git
cd mailcraft
make up
```

Open http://localhost:8025 in your browser, then:

```bash
make send-all          # Send all example templates
make send t=welcome    # Send a specific template
```

That's it. Your emails appear in the Mailpit inbox.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) (with Docker Compose)
- [Make](https://www.gnu.org/software/make/) (pre-installed on macOS/Linux)

## Commands

| Command | Description |
|---------|-------------|
| `make up` | Start Mailpit and the app |
| `make down` | Stop everything |
| `make send t=<name>` | Send a single template |
| `make send-all` | Send all templates |
| `make send t=<name> lang=ru` | Send in a specific language |
| `make list` | List available templates |
| `make new t=<name>` | Scaffold a new template |
| `make build` | Rebuild the Docker image |

## Project Structure

```
mailcraft/
├── CLAUDE.md              # AI rules for email template creation
├── Makefile               # All commands
├── Dockerfile
├── docker-compose.yml
├── send.py                # Template renderer + SMTP sender
├── requirements.txt
└── templates/
    ├── base.html          # Base layout (extend this)
    ├── assets/
    │   └── logo.png       # Shared logo (add yours here)
    ├── welcome/
    │   ├── email.html     # Template
    │   └── data.json      # Variables
    ├── password_reset/
    │   ├── email.html
    │   └── data.json
    └── verification_code/
        ├── email.html
        └── data.json
```

## Creating a Template

### 1. Scaffold

```bash
make new t=order_confirmation
```

This creates:
- `templates/order_confirmation/email.html` — starter template
- `templates/order_confirmation/data.json` — empty data file

### 2. Edit the template

Templates use [Jinja2](https://jinja.palletsprojects.com/) and extend `base.html`:

```html
{% extends "base.html" %}

{% block title %}{{ page_title }}{% endblock %}

{% block content %}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; color: #333333;">
      {{ body_text }}
    </td>
  </tr>
</table>
{% endblock %}
```

### 3. Add variables

Edit `data.json`:

```json
{
  "page_title": "Order Confirmed",
  "body_text": "Your order #12345 has been confirmed.",
  "company_name": "My Store"
}
```

### 4. Preview

```bash
make send t=order_confirmation
```

Open http://localhost:8025 to see the result.

## Translations (i18n)

Add translation files as `data.{lang}.json`:

```
templates/welcome/
├── email.html
├── data.json        # English (default)
├── data.ru.json     # Russian
└── data.es.json     # Spanish
```

Send in a specific language:

```bash
make send t=welcome lang=ru
make send-all lang=es
```

## Base Layout

The `base.html` template provides:
- Responsive 600px container
- Logo header
- Content area
- Footer with company name and year

Override any section with Jinja2 blocks: `title`, `content`, `footer`, `extra_styles`.

### Variables provided by the base layout

| Variable | Description | Default |
|----------|-------------|---------|
| `logo_url` | Logo image (auto-embedded) | CID-embedded |
| `year` | Current year | Auto |
| `company_name` | Your company name | "Your Company" |
| `footer_text` | Footer message | Generic message |

## Email HTML Tips

HTML emails are not web pages. Key rules:
- Use `<table>` for layout, not `<div>`
- All styles must be inline (`style="..."`)
- No flexbox, grid, or modern CSS
- Max width: 600px
- Use `padding` for spacing, not `margin`
- Always set `font-family` on every text element
- See [CLAUDE.md](CLAUDE.md) for comprehensive rules

## AI-Assisted Development

This project includes rules for AI coding assistants so they generate email-compatible HTML automatically (table layouts, inline styles, no modern CSS). Rules are provided for:

| Tool | Config file |
|------|-------------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `CLAUDE.md` |
| [OpenAI Codex](https://openai.com/index/codex/) | `AGENTS.md` |
| [GitHub Copilot](https://github.com/features/copilot) | `.github/copilot-instructions.md` |
| [Cursor](https://cursor.sh/) | `.cursorrules` |

The canonical rules live in `CLAUDE.md` — other files reference the same rules. If your AI tool reads a different config file, copy the rules from `CLAUDE.md`.

---

If you find this useful, give it a ⭐ on [GitHub](https://github.com/Anuarder/mailcraft) — it helps others discover it!

## License

[MIT](LICENSE)
