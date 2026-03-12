# Mailcraft — AI Rules for Email Template Creation

> These rules guide AI assistants (Claude, Copilot, etc.) when creating or editing email templates in this project.

## Project Overview

Mailcraft is a local email template development sandbox. It uses:
- **Jinja2** for HTML templating (runs inside Docker)
- **Mailpit** for email preview (web UI at http://localhost:8025)
- **Make** for all commands (`make up`, `make send`, etc.)

## Email HTML Rules

HTML emails are NOT like web pages. Email clients (Gmail, Outlook, Apple Mail) have severe rendering limitations. Follow these rules strictly:

### Layout

- **Use `<table>` for all layout** — no `<div>` for structural layout, no flexbox, no grid, no CSS positioning
- Every layout table must have: `role="presentation"`, `cellpadding="0"`, `cellspacing="0"`, `border="0"`
- Set widths on `<table>` or `<td>`, not on `<div>` or other elements
- **Max width: 600px** for the email container — this is the industry standard
- Use `align="center"` on `<td>` for horizontal centering
- Use `style="padding: ..."` on `<td>` for spacing — never use `margin` (unreliable in email clients)

### Styling

- **All styles must be inline** — no external stylesheets, no `<style>` blocks (except in `<head>` for responsive media queries)
- Use `style="..."` attribute on every element that needs styling
- Specify `font-family` on every text element (inheritance is unreliable across email clients)
- Always include a web-safe font stack: `font-family: Arial, Helvetica, sans-serif;`
- Colors must be hex values (`#333333`), not named colors or `rgb()`
- **No CSS shorthand** for `border` or `background` in Outlook — use longhand properties

### Typography

- Set `font-size`, `line-height`, `color`, and `font-family` on every `<td>` containing text
- Use `<br>` for line breaks instead of multiple `<p>` tags when possible
- Don't use custom fonts (@font-face) — they're unsupported in most email clients
- Links: always set `color` and `text-decoration` inline on `<a>` tags

### Images

- Always set `width`, `height`, `alt`, `style="display: block; border: 0;"` on `<img>`
- Use CID-embedded images (`src="cid:image_name"`) for logos and icons
- For background images, use `data:` URIs as fallback or embed them inline
- Keep total email size under 100KB (excluding images) for best deliverability

### Responsive Design

- Media queries go in `<head><style>` only — they're the one exception to "all inline"
- Use `max-width: 600px; width: 100%;` on the container table for fluid scaling
- Add `@media only screen and (max-width: 480px)` for mobile overrides
- Use `!important` in media queries (required to override inline styles)

### What NOT to Do

- No `<div>` for layout (use `<table>`)
- No `flexbox`, `grid`, or `position` (unsupported in Outlook, many webmail clients)
- No `margin` for spacing (use `padding` on `<td>`)
- No `background-image` on `<div>` (unreliable — use on `<td>` with VML fallback for Outlook if needed)
- No `<style>` blocks for critical styles (Gmail strips `<style>` in certain views)
- No JavaScript (stripped by all email clients)
- No `<form>` elements (stripped by most email clients)
- No CSS animations or transitions
- No SVG (poor email client support)
- No `calc()`, `var()`, or any modern CSS

## Template Structure

### File Organization

Each template is a directory under `templates/`:

```
templates/
  my_template/
    email.html      # Jinja2 template (extends base.html)
    data.json       # Default (English) variables
    data.ru.json    # Optional: Russian translation
    data.es.json    # Optional: Spanish translation
    assets/         # Optional: template-specific images
      banner.jpg
```

### Creating a New Template

1. Run `make new t=template_name` to scaffold
2. Edit `templates/template_name/email.html` — extend `base.html`
3. Edit `templates/template_name/data.json` — add template variables
4. Preview: `make send t=template_name`

### Template Variables

Templates use Jinja2 syntax: `{{ variable_name }}`

The base layout provides these variables (set in data.json):
- `logo_url` — provided automatically (CID-embedded)
- `year` — provided automatically
- `company_name` — your company name (default: "Your Company")
- `footer_text` — footer message

### Extending base.html

```html
{% extends "base.html" %}

{% block title %}{{ page_title }}{% endblock %}

{% block content %}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; color: #333333;">
      Your content here
    </td>
  </tr>
</table>
{% endblock %}
```

### Overridable Blocks

- `{% block title %}` — page title
- `{% block content %}` — main email content
- `{% block footer %}` — footer (has a default)
- `{% block extra_styles %}` — additional CSS in `<head>` (for media queries)

## i18n (Translations)

- Default language is English (`data.json`)
- Add translations as `data.{lang}.json` (e.g., `data.ru.json`, `data.es.json`)
- Send in a specific language: `make send t=welcome lang=ru`
- The data files contain ALL text — templates should have NO hardcoded strings

## Common Patterns

### Call-to-Action Button

```html
<td align="center" style="padding-bottom: 24px;">
  <a href="{{ cta_url }}" style="display: inline-block; padding: 12px 32px; background-color: #2563eb; color: #ffffff; font-family: Arial, Helvetica, sans-serif; font-size: 16px; font-weight: 600; text-decoration: none; border-radius: 6px;">
    {{ cta_text }}
  </a>
</td>
```

### Notice/Warning Box

```html
<td align="center" style="padding-bottom: 24px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td style="background-color: #fef3c7; border-radius: 6px; padding: 16px 24px; font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #92400e;">
        {{ notice_text }}
      </td>
    </tr>
  </table>
</td>
```

### Verification Code Display

```html
<td align="center" style="padding-bottom: 24px;">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td style="background-color: #f4f4f5; border-radius: 8px; padding: 20px 40px; font-family: 'Courier New', monospace; font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #18181b;">
        {{ code }}
      </td>
    </tr>
  </table>
</td>
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make up` | Start Mailpit and app containers |
| `make down` | Stop all containers |
| `make send t=<name>` | Send a single template |
| `make send-all` | Send all templates |
| `make send t=<name> lang=ru` | Send template in a specific language |
| `make list` | List available templates |
| `make new t=<name>` | Scaffold a new template |
| `make build` | Rebuild Docker image |
