# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A one-page marketing site for "Horizon Wealth Planning". It is a git repo pushed to `github.com/shakuarai/financialplanning` (branch `main`, over HTTPS).

- `index.html` is the entire site: HTML, CSS in a `<style>` tag and vanilla JS in a `<script>` tag.
- `README.md` is the public project overview: page sections, how to run it, editing tips and demo limitations. When a change alters behaviour, sections or edit instructions, update it too.

These are hard constraints from the original brief: no frameworks, no build tools, no external JS or CSS libraries, and everything stays in one file.

## Commands

There is no build, lint or test tooling.

- Open in the browser: `open index.html`
- Syntax-check the embedded JS. Node is **not** installed, so use macOS JavaScriptCore:
  ```sh
  python3 -c "import re;s=open('index.html').read();open('/tmp/a.js','w').write(re.search(r'<script>(.*)</script>',s,re.S).group(1))"
  osascript -l JavaScript -e 'ObjC.import("Foundation"); new Function($.NSString.stringWithContentsOfFileEncodingError("/tmp/a.js",4,null).js); "JS OK"'
  ```
- There is no test suite. Verify behaviour by hand in the browser at mobile, tablet (768px) and desktop (1024px) widths.

## Architecture

**Section markers.** The CSS, HTML and JS each use numbered comment banners (e.g. `/* 7. TESTIMONIALS CAROUSEL */`). Navigate by these rather than by line numbers. The CSS is mobile-first: base rules, then `@media (min-width: 768px)`, then `(min-width: 1024px)`, then a `prefers-reduced-motion` block. All colours and spacing are `:root` custom properties.

**JS.** A single IIFE holds one `init*` function per feature (`initNav`, `initFadeIn`, `initCounters`, `initCarousel`, `initEnquiryForm`, `initNewsletter`, `initBackToTop`, `setYear`). They are all called on `DOMContentLoaded`. The shared flags `prefersReducedMotion` and `hasIO` gate animation. Every IntersectionObserver use has a fallback that shows content immediately.

**Coupling that spans CSS, HTML and JS (the easy things to break):**
- **Carousel cards per view.** `perView()` in JS (using matchMedia at 768px and 1024px, giving 1 / 2 / 3 cards) must match the `.carousel__slide` `flex-basis` in each media query. The track moves by `translateX(-index * 100 / perView %)`. The dots are rebuilt when a breakpoint is crossed. Slides out of view get `aria-hidden` and `inert`.
- **Carousel content.** Each slide's `aria-label="n of N"` is hard-coded. The star SVGs are injected by JS into the empty `.stars` divs, so don't add stars by hand.
- **Hero stats.** The count-up reads `data-target`, `data-prefix` and `data-suffix`. Each stat also has a sibling `sr-only` span holding the final value, and both must be edited together.
- **Enquiry form validation.** Validation is keyed by field `name`:
  - Each field needs a `validators[name]` function that returns an error string, or `""` when valid.
  - Each field needs an error element `#{name}-error`, wired to the field with `aria-describedby`.
  - Add the field to the `data` object in the submit handler.
  - The radio group and the consent checkbox show their red border on a wrapper element rather than the input; `targetFor()` maps these.
  - The form is `novalidate`, so all checks happen in JS.
- **Nav active-link highlighting.** It observes `main section[id]` and matches on `href="#id"`. A new nav link only highlights if it points to a section inside `<main>`.
- **Fade-in.** Add the `.fade-in` class (optionally with `.delay-1` to `.delay-3`) to any element; `initFadeIn` picks it up automatically.

**Demo behaviour.** Both forms only `console.log` their data as JSON. The enquiry form fakes a 1.5s request with `setTimeout`, then replaces `#form-card` with a success message. User input is inserted with `textContent`; keep it that way. The contact details, avatars (pravatar.cc) and social links are placeholders, as are the hero photo (Unsplash). External images are blocked when the page is published as a claude.ai artifact.
