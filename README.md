# wskillw

**中文名：地煞七十二变 skill** · [中文版 README](README.zh-CN.md)

Personal archive of self-built skills, kept under Git for versioning, reuse, and
migration across agent environments.

## Structure

```
wskillw/
├── skills/
│   ├── research-reports/          # evidence-first multi-domain research reports
│   ├── web-ui-capture/            # capture web UI states -> offline HTML prototype
│   └── timesheet-batch-filling/   # draft work logs from attendance + Git evidence (redacted)
├── collections/
│   └── nvwa-examples/             # distilled persona/thinking-style skills (14 personas)
├── ARCHIVE.md                     # provenance and archive manifest
└── README.md
```

## Skills

| Skill | Purpose | Source |
|-------|---------|--------|
| `research-reports` | Evidence-first research reports across market, technical, and humanities profiles; ledger + validator + HTML/PDF pipeline | `D:\Alex\skill` |
| `web-ui-capture` | Capture observable website states and produce an offline interactive HTML prototype with mock data | `C:\Users\guoxi\.codex\skills\web-ui-capture` |
| `timesheet-batch-filling` | Draft and safely submit work logs from WeCom attendance, Git history, and daily reports | `C:\Users\guoxi\.codex\skills\timesheet-batch-filling` (redacted copy) |
| `nvwa-examples` | Distilled thinking-style skills for 14 public figures/operators | `C:\Users\guoxi\AppData\Roaming\devin\skills\nuwa-skill\examples` |

## Install

Copy the skill directory into the target agent's skill root:

```bash
# WorkBuddy
cp -r skills/research-reports ~/.workbuddy/skills/

# Codex
cp -r skills/web-ui-capture ~/.codex/skills/
cp -r skills/timesheet-batch-filling ~/.codex/skills/

# nvwa personas (reference collection)
cp -r collections/nvwa-examples/* ~/.devin/skills/nuwa-skill/examples/
```

Each skill keeps its own `SKILL.md` at the directory root.

## Redactions and exclusions

- **`timesheet-batch-filling` is redacted.** The internal work-log host is replaced
  with `${WORKLOG_BASE_URL}` and the example project name with `<PROJECT_NAME>`.
  No credentials, tokens, cookies, or passwords are included. The original remains
  at `C:\Users\guoxi\.codex\skills\timesheet-batch-filling`.
- **`nvwa-examples/trump-perspective` is not included** in this public archive. It
  remains at the source path. The other 14 persona skills are included.
- **`research-reports` exclusions.** `AGENTS.md` and the two
  `代码生成视频方法论-*.md` files were excluded because they are not part of the
  skill. The skill's `SKILL.md`, `core/`, `profiles/`, `scripts/`, `assets/`,
  `references/`, and `samples/` are included.
- **Caches and local state** (`__pycache__`, `.pytest_cache`, `.env`, logs) are
  ignored via `.gitignore`.

## Conventions

- One skill per directory, with `SKILL.md` at the root.
- No secrets, internal hosts, customer data, or personal tokens.
- Large sample outputs are allowed only when they are part of the skill's
  documentation; keep the repository under a few megabytes where possible.
- Changes are committed with a short message describing the skill and the change.

## Ownership

Personal archive. No open-source license is declared; all rights remain with the
owner unless a skill states otherwise.
