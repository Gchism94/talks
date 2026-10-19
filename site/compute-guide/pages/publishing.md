# Publishing options

**Decision: use Zensical for this guide and keep GitHub Pages hosting.** It supplies search and consistent navigation; the needs tool remains a small browser-only component. No paid platform or new account is needed.

## What we compared

| Option | Best use | Tradeoff for this site |
| --- | --- | --- |
| **Zensical — selected** | Resource guides with search, sidebars and Markdown content | Python-based workflow fits the existing builders. Custom CSS/JS is supported. Pin the version and check compatibility before upgrades. |
| **Astro Starlight** | Documentation with richer custom components | Built-in search and accessible navigation; strong component flexibility. Adds a Node/Astro content and build workflow. |
| **Quarto** | Reports, notebooks and teaching materials published together | Good scientific authoring, navigation and search. Adds the Quarto toolchain; useful if executable reports become central. |
| **Custom HTML, as before** | A distinctive small landing page | Maximum control, but navigation, search and page consistency require ongoing custom work. |

These are publishing engines, not compute providers. Any can produce static files for GitHub Pages. Moving the authoring system does not create teaching compute or durable institutional ownership of the hosting service.

## Design reference

[MESA’s public site](https://idss-mesa.github.io/) uses direct headings, open space, simple links and short sections. Its landing page links to a separate documentation area. This guide adopts that clarity while keeping Arizona navy/red accents, searchable resources and a consistent page structure. It is not a copy of MESA or a claim of institutional service approval.

## Maintenance

- Build with **Zensical 0.0.71**, pinned for this release; published files stay in the existing repository.
- Keep factual sources in the evidence ledger and the public guide concise.
- Preserve existing page addresses, downloads and the five-slide talk.
- Test search, mobile navigation and the needs tool before upgrading. Zensical is currently a 0.x product; unsupported MkDocs plugins are not automatically compatible.
- Built-in client-side search requires JavaScript. Core information and links remain readable without it.

## Primary references

Reviewed October 19, 2026. This is a site-fit assessment, not a performance benchmark.

- [Zensical installation](https://zensical.org/docs/) · [custom JavaScript/CSS](https://zensical.org/docs/customization/) · [search](https://zensical.org/docs/setup/search/) · [GitHub Pages publishing](https://zensical.org/docs/publish-your-site/)
- [Zensical compatibility and migration](https://zensical.org/docs/compatibility/mkdocs/migration/) · [supported plugins](https://zensical.org/docs/compatibility/mkdocs/plugins/)
- [Astro Starlight features](https://starlight.astro.build/)
- [Quarto websites and publishing](https://quarto.org/docs/websites/)
