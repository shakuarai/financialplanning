#!/usr/bin/env python3
"""Keep the Content-Security-Policy hashes in index.html in sync.

The CSP only allows the inline <style> and <script> whose SHA-256 hash it
lists, so any edit to either block needs new hashes or the page loses its
styles or JS.

  python3 tools/csp-hashes.py          # rewrite the hashes in index.html
  python3 tools/csp-hashes.py --check  # exit 1 if they are out of date
"""
import base64
import hashlib
import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"


def sha256(text):
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode() + "'"


def main():
    html = PAGE.read_text(encoding="utf-8")
    # Plain <style> and <script> only; the JSON-LD block has a type attribute and isn't executed
    style = sha256(re.search(r"<style>(.*?)</style>", html, re.S).group(1))
    script = sha256(re.search(r"<script>(.*?)</script>", html, re.S).group(1))

    updated = re.sub(r"script-src 'sha256-[^']+'", "script-src " + script, html, count=1)
    updated = re.sub(r"style-src 'sha256-[^']+'", "style-src " + style, updated, count=1)

    if "--check" in sys.argv:
        if updated != html:
            print("CSP hashes are out of date. Run: python3 tools/csp-hashes.py")
            sys.exit(1)
        print("CSP hashes OK")
        return

    PAGE.write_text(updated, encoding="utf-8")
    print("style ", style)
    print("script", script)


if __name__ == "__main__":
    main()
