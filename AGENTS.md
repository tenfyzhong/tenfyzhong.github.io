# Repository Guidelines

This document provides guidelines for contributing to tenfy's blog repository. It is a static site built with Hugo.

## Project Structure & Module Organization

- **Configuration**: `hugo.yaml` controls site settings.
- **Content**: `content/` contains Markdown files for blog posts and pages.
- **Themes**: `themes/maupassant-hugo/` contains the site theme (submodule).
- **Archetypes**: `archetypes/` defines templates for new content.
- **Output**: `public/` is the build destination (not tracked in git).

## Build, Test, and Development Commands

- `hugo server -D`: Starts the local development server at `http://localhost:1313/`. The `-D` flag includes draft content.
- `hugo --gc --minify`: Builds the static site for production, cleans the cache, and minifies resources.
- `hugo new content posts/my-post.md`: Creates a new blog post file using the default archetype.

## Coding Style & Naming Conventions

- **Content**: Use Markdown for all posts. Frontmatter must be in YAML format.
- **Language**: The primary language is Simplified Chinese (`zh-CN`).
- **File Naming**: Use kebab-case for filenames (e.g., `my-new-post.md`).
- **Formatting**: Ensure files are UTF-8 encoded.

## Post Taxonomy Guidelines

- Treat `categories` as a controlled vocabulary. Each post should have exactly one primary category in Chinese.
- Use only these canonical categories:
  - `人工智能`: LLMs, AI workflows, model/API usage, or AI-enhanced toolchains.
  - `工具`: Editors, CLI tools, productivity utilities, and standalone tool introductions.
  - `网络技术`: DNS, TCP/IP, packet capture, traffic analysis, and network architecture.
  - `运维`: Deployment, containers, observability, service operations, and server administration.
  - `编程语言`: Language-specific syntax, idioms, toolchains, libraries, and code-level practices.
  - `数据库`: Databases, replication, indexing, storage/query behavior, and data-layer tuning.
  - `操作系统`: OS-level workflows, boot/install media, process control, and system mechanics.
  - `后端开发`: Backend architecture, algorithms, timeout/queue design, and service-side engineering topics that are not primarily language tutorials or ops guides.
- Do not create vague, overly specific, or English category names such as `技术`, `Golang`, or `Vim`.
- Normalize legacy category values when touching old posts:
  - `Golang` -> `编程语言`
  - `Vim` -> `工具`
  - `技术` -> replace with the most specific canonical category. In the current content set, deployment-oriented posts such as `deploy-n8n-on-hf.md` should fall under `运维`.
- Treat `tags` as controlled but extensible metadata. Use 2-5 tags per post, all in lowercase English `kebab-case`.
- Prefer a tag mix of:
  - one product/tool/framework tag, such as `docker`, `cloudflare`, `openclaw`
  - one or two technical/topic tags, such as `dns`, `json`, `shared-memory`, `load-balancing`
  - one environment or article-form tag when it adds signal, such as `linux`, `macos`, `tutorial`, `benchmark`
- Avoid tags that only restate the category (`network`, `database`, `tools`, `ai`) unless the post spans categories and the umbrella tag materially improves discovery.
- Do not use spaces, Chinese, title case, or promotional wording in tags.
- Normalize legacy tag values when touching old posts:
  - `JSON` -> `json`
  - `Benchmark` -> `benchmark`
  - `hugging face` -> `hugging-face`
  - `hf spaces` -> `hugging-face-spaces`
  - `性能优化` -> `performance`
  - `自动化` -> `automation`
  - `免费部署` -> `free-tier` if the free-tier angle is central; otherwise omit it
- When a post could fit multiple categories, choose the dominant reader intent:
  - Go/Python-specific code topics -> `编程语言`
  - Deployment/runbook/operations topics -> `运维`
  - Vim/fish/homebrew/Dash-style usage posts -> `工具`
  - Protocol/packet/DNS topics -> `网络技术`

## Testing Guidelines

- **Visual Verification**: Use `hugo server` to verify layout and rendering locally before committing.
- **Drafts**: Mark incomplete posts with `draft: true` in the frontmatter.
- **Validation**: Ensure all local links and image references work correctly.

## Commit & Pull Request Guidelines

- **Commit Messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/).
  - Format: `type(scope): description`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
  - Examples:
    - `feat(content): add JSON benchmark comparison post`
    - `docs: update installation guide`
  - Include a detailed body/footer for complex changes.
- **Pull Requests**: Target the `source` branch (source of truth). Ensure the site builds cleanly before merging.
