# staten-extensions

Personal [Claude Code](https://claude.com/claude-code) extensions, packaged as a
plugin marketplace so they install on any machine.

## Layout

```
.claude-plugin/marketplace.json     # marketplace: lists every plugin below
plugins/
  jira-cloud-tools/                 # a plugin (has its own README)
    .claude-plugin/plugin.json
    reference/                      # shared, e.g. definition-of-ready.md
    skills/analyze-ticket/          # SKILL.md + scripts/ + reference/
    skills/ready-check-ticket/      # gated readiness runner
    skills/challenge-readiness/     # internal critic (hidden)
```

One repo = one marketplace = many plugins. Each plugin can bundle skills,
agents, commands, and hooks, and documents itself in its own README. Add new
plugins under `plugins/`.

## Add the marketplace

```
/plugin marketplace add Erchamion/claude-extensions
```

To pull in later changes: `/plugin marketplace update staten-extensions`.

## Plugins

| Plugin | What it does | Docs |
|--------|--------------|------|
| **jira-cloud-tools** | Analyze a single Jira Cloud ticket (read-only) and produce a type-aware analysis. | [README](plugins/jira-cloud-tools/README.md) |

Install a plugin with `/plugin install <name>@staten-extensions` — see each
plugin's README for its install command, prerequisites, and configuration.

## License

[MIT](LICENSE) © 2026 Jon Staten
