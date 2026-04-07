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
- **Categories**: Use exactly one canonical Chinese category per post: `人工智能` / `工具` / `网络技术` / `运维` / `编程语言` / `数据库` / `操作系统` / `后端开发`.
- **Category boundaries**: Language-centric topics belong to `编程语言`; deployment/observability topics belong to `运维`; editor/CLI/tool workflow posts belong to `工具`; DNS/packet/protocol topics belong to `网络技术`.
- **Do not use legacy categories**: Avoid `技术`, `Golang`, `Vim`. Normalize them to the canonical set when touching older posts.
- **Tags**: Prefer 2-4 tags, all lowercase English in `kebab-case`. No Chinese, spaces, or title case.
- **Tag composition**: Prefer `product/tool + technical topic + environment or article form`, for example `docker`, `dns`, `linux`, `tutorial`.
- **Tag reuse**: Prefer tags that can group multiple posts or represent durable technologies. Avoid one-off scenario tags unless they are likely to recur.
- **Avoid near-duplicates**: If a broader tag like `docker` already captures the topic, do not add a narrower sibling like `docker-compose` unless that narrower axis is central and reusable.
- **Normalize legacy tags**: `JSON` -> `json`, `Benchmark` -> `benchmark`, `hugging face` -> `hugging-face`, `hf spaces` -> `hugging-face-spaces`, `性能优化` -> `performance`, `自动化` -> `automation`.
- **Avoid redundant umbrella tags**: Do not add tags like `tools`, `network`, `database`, or `ai` if they only repeat the category and do not improve discovery.
