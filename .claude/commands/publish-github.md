---
description: Security-scan the project, push it to GitHub, update the README and repo About, and deploy GitHub Pages via Actions
argument-hint: "[owner/repo] [public|private] [commit message]"
allowed-tools: Bash(git:*), Bash(gh:*), Bash(grep:*), Bash(find:*), Bash(ls:*), Bash(cat:*), Bash(du:*), Bash(file:*), Bash(python3:*), Bash(osascript:*), Bash(curl:*), Bash(mkdir:*), Bash(gitleaks:*), Bash(trufflehog:*), Read, Write, Edit
---

Publish this project to GitHub and host it on GitHub Pages.

Arguments (all optional): `$ARGUMENTS`
- `owner/repo`: target repository. Default: the existing `origin` remote; if there is none, `<gh user>/<folder name>`.
- `public|private`: visibility, used only when the repo has to be created. Default: `public` (GitHub Pages on a free plan needs a public repo).
- Any remaining text is the commit message. Default: write a short, accurate message from the diff.

Work through the steps **in order**. Nothing may leave this machine until step 1 has passed. If a step fails, stop and report what failed with the command output; do not work around it silently.

## 0. Preflight

1. Run `gh auth status`. If not logged in, stop and tell the user to run `gh auth login`.
2. If the folder is not a git repo, run `git init -b main`.
3. Record: current branch, `git remote -v`, `git status --porcelain`, and whether the target repo already exists (`gh repo view <owner/repo> --json name,visibility,description,homepageUrl,repositoryTopics`).
4. Make sure `.gitignore` exists and covers at least: `.DS_Store`, `.env*`, `*.pem`, `*.key`, `node_modules/`, `.claude/settings.local.json`. Keep any existing entries (e.g. `CLAUDE.md`). Don't ignore `.claude/commands/` unless the user asks.

## 1. Security scan (gate: must pass before any push or API write)

Scan **exactly the set of files that would be pushed**: tracked files plus untracked, non-ignored files (`git ls-files -co --exclude-standard`). Also scan git history for anything already committed but not yet on the remote (`git log -p origin/<branch>..HEAD`, or the full `git log -p` if there is no remote).

Checks:
1. **Secret scanners.** If `gitleaks` is installed, run `gitleaks detect --no-banner -v` (and `gitleaks protect --staged`). If `trufflehog` is installed, run `trufflehog filesystem . --only-verified`. If neither is installed, say so and rely on the checks below.
2. **Secret patterns** (grep, case-insensitive where sensible) in the files and the unpushed history:
   - Private keys: `-----BEGIN [A-Z ]*PRIVATE KEY-----`
   - Cloud/API tokens: `AKIA[0-9A-Z]{16}`, `ghp_|gho_|ghu_|ghs_|github_pat_`, `sk-[A-Za-z0-9_-]{20,}`, `sk-ant-`, `xox[baprs]-`, `AIza[0-9A-Za-z_-]{35}`, `sk_live_|pk_live_|rk_live_`
   - Generic assignments: `(api[_-]?key|secret|token|password|passwd|client[_-]?secret)\s*[:=]\s*['"][^'"]{8,}`
   - Credentials in URLs: `[a-z]+://[^/\s:@]+:[^/\s@]+@`
3. **Sensitive files**: `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa*`, `*.sqlite`, `*.db`, `credentials*`, `*.log`, `.DS_Store`, backup files (`*.bak`, `*~`).
4. **Personal data**: real-looking email addresses, phone numbers and street addresses. The ones documented as placeholders in the README / `WealthPlanning` §6 are fine; flag anything else, including the user's own email if it appears.
5. **Large files**: anything over 5 MB (`find . -path ./.git -prune -o -type f -size +5M -print`).
6. **Site-specific checks for `index.html`**:
   - External `<script src>` or stylesheet `<link>` (the brief allows none) and any `http://` (non-HTTPS) resource URLs.
   - Forms must not post to a real endpoint (both forms are demo-only and should just `console.log`).
   - User input must be inserted with `textContent`; flag any new `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` or `eval` that touches user input.
   - External links with `target="_blank"` should have `rel="noopener"` (or `noreferrer`).
   - Syntax-check the embedded JS with the JavaScriptCore command in `CLAUDE.md`.
7. **Workflow check**: any `.github/workflows/*.yml` must use least-privilege `permissions`, must not echo secrets, and must pin actions to a major version from the official `actions/` org.

Report the results as a short table (check, result, details). Then:
- **Any secret, private key or credential found** → STOP. Don't push. Tell the user which file and line, and how to remove it (for history, that means rewriting it and rotating the secret).
- **Only warnings** (personal data, large files, missing `rel="noopener"`, etc.) → list them and ask the user whether to fix them, continue anyway or abort. Fix only what they approve.
- **Clean** → continue.

## 2. README

Create `README.md` if missing, otherwise update it in place, preserving what's still accurate and the author's wording. It should cover:
- Title and a one-paragraph description of the project.
- **Live site** link: `https://<owner>.github.io/<repo>/` (use `gh api repos/<owner>/<repo>/pages --jq .html_url` once Pages exists).
- Features, tech notes (single file, no frameworks, no build), how to run locally (`open index.html`), and the deployment method (GitHub Pages via Actions, see `.github/workflows/pages.yml`).
- A note that contact details, avatars and social links are placeholders.

Base the content on `index.html`, `CLAUDE.md` and `WealthPlanning` where present. Don't invent features.

## 3. GitHub Pages workflow

Create or update `.github/workflows/pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - name: Assemble site
        run: |
          mkdir -p _site
          cp index.html _site/
          touch _site/.nojekyll
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site
      - id: deployment
        uses: actions/deploy-pages@v4
```

Only publish the site files (`index.html` plus any assets it references), never the whole repo, so docs and tooling files are not served. If the default branch isn't `main`, change the trigger to match.

## 4. Commit and push

1. Show the user the final file list (`git status --short`) and the commit message.
2. **Confirm before the first push to a repo, before creating a repo, and before making a repo public.** On later runs to the same, already-existing repo, a push after a clean scan needs no extra confirmation.
3. Stage explicitly by path (never `git add -A` blindly after the scan; stage only what was scanned). Commit with the message, ending with the attribution line required by the current session, if any.
4. If the repo doesn't exist: `gh repo create <owner/repo> --<visibility> --source=. --remote=origin --push`. Otherwise `git push -u origin <branch>`. Never force-push; if the push is rejected, stop and report.

## 5. Enable Pages (Actions source)

```sh
gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow   # first time
gh api -X PUT  repos/<owner>/<repo>/pages -f build_type=workflow   # if it already exists with another source
```

Then watch the deploy: `gh run list --workflow=pages.yml -L 1` and `gh run watch <id> --exit-status`. If it fails, show `gh run view <id> --log-failed` and stop.

Get the live URL: `gh api repos/<owner>/<repo>/pages --jq .html_url`.

## 6. Repo About (description, website, topics)

```sh
gh repo edit <owner/repo> \
  --description "<one-line description, max ~120 chars>" \
  --homepage "<pages html_url>" \
  --add-topic <topic> ...
```

- Description: derived from the README's first paragraph.
- Homepage: the GitHub Pages URL from step 5. This is what puts the Pages link in the repo's About panel.
- Topics: 3–6 lowercase, relevant ones (e.g. `html`, `css`, `javascript`, `static-site`, `github-pages`, `landing-page`). Keep existing topics unless clearly wrong.

If step 2's README still has a placeholder Pages URL, fix it now, commit ("Add live site link to README") and push.

## 7. Verify and report

1. `curl -sI <pages url>` returns 200 (Pages can take a minute after the first deploy; retry a few times).
2. `gh repo view <owner/repo> --json description,homepageUrl,repositoryTopics` shows the new values.

Finish with a short summary: security scan outcome (and any warnings the user accepted), commit SHA pushed, repo URL, live site URL, and anything skipped or still needing attention.
