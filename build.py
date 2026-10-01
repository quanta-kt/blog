#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["markdown-it-py", "pygments", "jinja2"]
# ///
"""Build the blog: content/p/*.md -> build/. Run with: uv run build.py"""
import datetime as dt
import shutil
import tomllib
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markdown_it import MarkdownIt
from markupsafe import Markup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "build"


@dataclass
class Post:
    slug: str
    title: str
    date: dt.datetime
    html: Markup
    description: str = ""

    @property
    def url(self):
        return f"/p/{self.slug}/"


def parse(path):
    """Split a '+++' TOML frontmatter block from the markdown body."""
    _, head, body = path.read_text().split("+++\n", 2)
    return tomllib.loads(head), body


def as_datetime(d):
    """TOML gives a date, a datetime, or a quoted string; normalise to aware datetime."""
    if isinstance(d, str):
        d = dt.datetime.fromisoformat(d)
    elif not isinstance(d, dt.datetime):
        d = dt.datetime(d.year, d.month, d.day)
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def fence(self, tokens, idx, options, env):
    tok = tokens[idx]
    lang = tok.info.strip().split(" ")[0]
    try:
        lexer = get_lexer_by_name(lang)
    except ClassNotFound:
        lexer = TextLexer()
    code = highlight(tok.content, lexer, HtmlFormatter(nowrap=True)).rstrip("\n")
    return f"<pre><code>{code}</code></pre>\n"


def image(self, tokens, idx, options, env):
    """Inline .svg images so they can carry their own styles and scripts."""
    src = tokens[idx].attrGet("src")
    if src.endswith(".svg"):
        return (ROOT / src.lstrip("/")).read_text()
    return self.image(tokens, idx, options, env)


def main():
    site = tomllib.loads((ROOT / "config.toml").read_text())
    now = dt.datetime.now(dt.timezone.utc)
    md = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    md.add_render_rule("fence", fence)
    md.add_render_rule("image", image)

    posts = []
    for path in (ROOT / "content" / "p").glob("*.md"):
        meta, body = parse(path)
        date = as_datetime(meta["date"])
        if date > now:
            continue
        posts.append(Post(path.stem, meta["title"], date, Markup(md.render(body)), meta.get("description", "")))
    posts.sort(key=lambda p: p.date, reverse=True)

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(ROOT / "static", OUT / "static")
    (OUT / "index.html").write_text(env.get_template("home.html").render(site=site, posts=posts))
    (OUT / "feed.xml").write_text(env.get_template("feed.xml").render(site=site, posts=posts, updated=posts[0].date if posts else now))
    for p in posts:
        out = OUT / "p" / p.slug
        out.mkdir(parents=True)
        (out / "index.html").write_text(env.get_template("post.html").render(site=site, post=p))
    print(f"built {len(posts)} posts")


if __name__ == "__main__":
    main()
