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
