from __future__ import annotations

from html import unescape
from html.parser import HTMLParser


class JobContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lines: list[str] = []
        self._tag_stack: list[str] = []
        self._current: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag)
        if tag in {"p", "li", "h1", "h2", "h3"}:
            self._current = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "li", "h1", "h2", "h3"}:
            self._flush(tag)
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        text = " ".join(unescape(data).split())
        if text:
            self._current.append(text)

    def _flush(self, tag: str) -> None:
        text = " ".join(self._current).strip()
        self._current = []
        if not text:
            return
        if tag in {"h1", "h2", "h3"}:
            self.lines.append(f"**{text}**")
        elif tag == "li":
            self.lines.append(f"- {text}")
        else:
            self.lines.append(text)


def html_to_markdownish(value: str) -> str:
    parser = JobContentParser()
    parser.feed(unescape(value))
    parser.close()
    return "\n\n".join(parser.lines)

