#!/usr/bin/env python3
"""Render Jinja2 email templates and send them to Mailpit via SMTP."""

import base64
import json
import mimetypes
import os
import smtplib
import sys
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"
SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@example.com")
TO_EMAIL = os.environ.get("TO_EMAIL", "dev@example.com")


def get_template_names() -> list[str]:
    """Return sorted list of template folder names."""
    return sorted(
        d.name
        for d in TEMPLATES_DIR.iterdir()
        if d.is_dir() and (d / "email.html").exists()
    )


def load_data(name: str, lang: str = "en") -> dict:
    """Load data file for a template. Tries data.{lang}.json first, falls back to data.json."""
    if lang != "en":
        lang_file = TEMPLATES_DIR / name / f"data.{lang}.json"
        if lang_file.exists():
            with open(lang_file) as f:
                return json.load(f)

    data_file = TEMPLATES_DIR / name / "data.json"
    if data_file.exists():
        with open(data_file) as f:
            return json.load(f)
    return {}


def image_to_data_uri(file_path: Path) -> str:
    """Convert an image file to a base64 data URI."""
    if not file_path.exists():
        return ""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "application/octet-stream"
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def render_template(name: str, data: dict) -> str:
    """Render a Jinja2 template with its data context."""
    shared = {
        "logo_url": "cid:logo",
        "year": "2026",
    }

    logo_path = TEMPLATES_DIR / "assets" / "logo.png"
    if logo_path.exists():
        shared["logo_url"] = "cid:logo"

    merged = {**shared, **data}
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template(f"{name}/email.html")
    return template.render(**merged)


def attach_image(msg: MIMEMultipart, file_path: Path, cid: str) -> None:
    """Attach an image file as a CID-embedded inline image."""
    if not file_path.exists():
        print(f"  Warning: image not found: {file_path}")
        return

    mime_type, _ = mimetypes.guess_type(str(file_path))
    subtype = mime_type.split("/")[1] if mime_type else "octet-stream"

    with open(file_path, "rb") as f:
        img = MIMEImage(f.read(), _subtype=subtype)

    img.add_header("Content-ID", f"<{cid}>")
    img.add_header("Content-Disposition", "inline", filename=file_path.name)
    msg.attach(img)


def send_email(name: str, lang: str, html: str, data: dict) -> None:
    """Send rendered HTML email with embedded images to Mailpit."""
    msg = MIMEMultipart("related")
    lang_label = f" [{lang}]" if lang != "en" else ""
    msg["Subject"] = f"[Preview] {name}{lang_label}"
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    msg_alt = MIMEMultipart("alternative")
    msg_alt.attach(MIMEText(html, "html"))
    msg.attach(msg_alt)

    logo_path = TEMPLATES_DIR / "assets" / "logo.png"
    if logo_path.exists():
        attach_image(msg, logo_path, "logo")

    template_assets = TEMPLATES_DIR / name / "assets"
    if template_assets.exists():
        for asset_file in sorted(template_assets.iterdir()):
            if asset_file.is_file() and not asset_file.name.startswith("."):
                cid = asset_file.stem
                attach_image(msg, asset_file, cid)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())

    print(f"  Sent: {name} ({lang})")


def cmd_send(name: str, lang: str = "en") -> None:
    """Render and send a single template."""
    if name not in get_template_names():
        print(f"Error: template '{name}' not found.")
        print(f"Available: {', '.join(get_template_names())}")
        sys.exit(1)

    data = load_data(name, lang)
    html = render_template(name, data)
    send_email(name, lang, html, data)


def cmd_send_all(lang: str = "en") -> None:
    """Render and send all templates."""
    names = get_template_names()
    if not names:
        print("No templates found.")
        sys.exit(1)

    for name in names:
        data = load_data(name, lang)
        html = render_template(name, data)
        send_email(name, lang, html, data)

    print(f"\n  Done: {len(names)} email(s) sent ({lang}).")


def cmd_list() -> None:
    """List all available templates."""
    names = get_template_names()
    if not names:
        print("No templates found.")
        return

    print("Available templates:")
    for name in names:
        template_dir = TEMPLATES_DIR / name
        langs = ["en"]
        for f in sorted(template_dir.glob("data.*.json")):
            lang_code = f.stem.split(".")[-1]
            langs.append(lang_code)
        print(f"  - {name} ({', '.join(langs)})")


def parse_lang(args: list[str]) -> str:
    """Extract --lang value from args, default to 'en'."""
    for i, arg in enumerate(args):
        if arg == "--lang" and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith("--lang="):
            return arg.split("=", 1)[1]
    return "en"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python send.py send <template-name> [--lang ru]")
        print("  python send.py send-all [--lang ru]")
        print("  python send.py list")
        sys.exit(1)

    command = sys.argv[1]
    lang = parse_lang(sys.argv)

    if command == "send":
        if len(sys.argv) < 3:
            print("Error: template name required.")
            print("Usage: python send.py send <template-name> [--lang ru]")
            sys.exit(1)
        cmd_send(sys.argv[2], lang)
    elif command == "send-all":
        cmd_send_all(lang)
    elif command == "list":
        cmd_list()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
