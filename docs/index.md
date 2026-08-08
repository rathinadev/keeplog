---
description: keeplog records every terminal command and its output to a searchable local SQLite database. Install once, search your shell history instantly with fzf.
---

<div class="hero">
  <div class="hero-content">
    <div class="hero-badge">v1.0.0 • Open Source • MIT</div>
    <h1>Never lose a command again.</h1>
    <p class="hero-subtitle">
      keeplog records every shell command + output in the background.<br>
      Search everything instantly with full-text search.
    </p>
    <div class="hero-actions">
      <a href="#install" class="md-button md-button--primary">Get Started</a>
      <a href="https://github.com/rathinadev/keeplog" class="md-button">GitHub</a>
    </div>
    <div class="hero-terminal">
      <div class="terminal-bar">
        <span class="terminal-dot red"></span>
        <span class="terminal-dot yellow"></span>
        <span class="terminal-dot green"></span>
        <span class="terminal-title">keeplog record</span>
      </div>
      <div class="terminal-body">
        <span class="prompt">$</span> <span class="cmd">docker build -t app .</span>
        <span class="output">[+] Building 12.5s (8/8) FINISHED</span>
        <span class="prompt">$</span> <span class="cmd">keeplog search "docker build"</span>
        <span class="output">  [42] docker build -t app .  12.5s  exit:0</span>
        <span class="cursor">█</span>
      </div>
    </div>
  </div>
</div>

---

## Install

```bash
pip install keeplog
keeplog setup
```

## Features

<div class="grid cards" markdown>

-   :material-console-line: **PTY Capture** — records full output, not just commands
-   :material-database-search: **Full-Text Search** — instant across everything via SQLite FTS5
-   :material-code-tags: **No Dependencies** — pure Python, stdlib only
-   :material-lightning-bolt: **Lightweight** — zero config, install and forget
-   :material-apple: **Cross-Platform** — macOS + Linux, zsh + bash + fish
-   :material-github: **Open Source** — MIT license

</div>

## Quick Start

```bash
# Record a session
keeplog record

# In another terminal, search while recording
keeplog search docker
```

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "keeplog",
  "description": "Terminal session logger with full-text search. Records every shell command and output to a local SQLite database.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "macOS, Linux",
  "url": "https://rathinadev.github.io/keeplog/",
  "downloadUrl": "https://pypi.org/project/keeplog/",
  "license": "https://github.com/rathinadev/keeplog/blob/main/LICENSE",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
</script>
