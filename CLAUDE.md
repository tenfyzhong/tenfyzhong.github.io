# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Run development server**: `hugo server -D` (includes drafts)
- **Build site**: `hugo --gc --minify`
- **New content**: `hugo new content posts/my-new-post.md`

## Architecture

- **Static Site Generator**: Hugo
- **Configuration**: `hugo.yaml`
- **Theme**: `maupassant-hugo` (in `themes/` directory)
- **Content**: Located in `content/`.
- **Output**: Built site goes to `public/` (ignored by git, deployed via CI)

## Deployment

- **CI/CD**: GitHub Actions workflow in `.github/workflows/hugo.yaml`
- **Target**: GitHub Pages
- **Branch**: `source` branch is the source of truth; deployments happen on push to `source`.

## Content Guidelines

- **Frontmatter**: YAML format.
- **Language**: `zh-CN` (Chinese, Simplified).
- **Drafts**: Set `draft: true` in frontmatter to prevent publication. Use `-D` flag with `hugo server` to view locally.
