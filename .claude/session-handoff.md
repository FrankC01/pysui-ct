# Session Handoff — pysui-ct

## Project starting state (2026-07-07)

Repo created via seed brief pasted in-session (carried over from the pysui-token/pysui #79 context). See `.claude/CLAUDE.md` for the full why-this-exists / three-tier chain / boundary description. This file tracks in-progress state only; durable architecture facts live in `.claude/CLAUDE.md`.

### Why this exists (summary)

Unblocks pysui Plan #79 (PrivateFunds / ConfidentialTransfer client work). This repo is the middle tier of a three-tier chain (pysui-token -> pysui-ct -> pysui #79): it vendors Mysten Labs' Confidential Transfer Move contracts onto devnet and exposes a management CLI, so CT client work in pysui can proceed before Mysten deploys CT to a public network (targeted ~Aug/Sept 2026).

### Decisions locked at kickoff

- Repo name and location: `pysui-ct`, sibling to `pysui-token` (`~/frankc01/pysui-ct`).
- Management CLI: pysui-driven (dogfooded), dedicated venv pinned to pysui 1.1.0, UCI compliant. Reuses the `console/` structure from `~/frankc01/pysui-token/console/`.
- Move contracts: Frank copies the actual Mysten CT Move contracts in manually — not vendored or looked up by an agent.
- Network: devnet.
- Boundary: this project's only public output is `package_id`, `token_registry`, and `account_registry` — consumed by pysui #79's `PrivateFundsGroup` (`pysui/private_transfer/config.py`), replacing Ben Riva's placeholder `0x` addresses.
- Backlog is per-project, lives at `~/.claude/projects/-Users-fastfrank-frankc01-pysui-ct/memory/project_change_opportunities.md`, seeded with item #1 ("Confidential Transfer Contract", priority 1, Release Target 0.1.0).

### Housekeeping completed (2026-07-07)

- `CLAUDE.md` convention: full content lives in `.claude/CLAUDE.md`; root `CLAUDE.md` is a one-line stub pointing to it.
- Backlog file created (see above), seeded with item #1; `MEMORY.md` seeded in this project's own auto-memory directory.
- `.claude/settings.json` and `.claude/settings.local.json` copied from `~/frankc01/pysui-token/.claude/`: broad `Bash`/`Read`/`Write`/`Edit` allow in `settings.json`; `defaultMode: bypassPermissions` plus existing allow entries in `settings.local.json`. Requires a Claude Code restart to take effect.

### Task 1 completed (2026-07-07) — Confidential Transfer Contract

- Mysten's CT Move contracts vendored into `contracts/sources/` (10 modules: contra, policy, balance, encrypted_amount, twisted_elgamal, nizk, auditors, deny_list, decode, events). A stray `Published.toml` copied in by mistake (stale Mysten devnet metadata, chain-id mismatched with `Move.toml`) was identified and deleted by Frank.
- `console/` scaffolded mirroring `pysui-token/console/`'s layout (`__init__.py`, `__main__.py`, `cmd_args.py`, `cmds.py`), with a `publish` subcommand.
- `contra` published to devnet. IDs captured as module-level defaults in `console/cmds.py`:
  - `package_id`: `0xdbf579054d6a93d3eca02d549cf16d4008475c8930fdfda40bef763a7385fff1`
  - `token_registry`: `0x5fde83596901ff336e065e63b9212a3ff066a6b74a3c0ce2f4af3708df636638`
  - `account_registry`: `0xebf3a594bd19565ff273bd99251e8ca33469b178eb45c0a9acaccf7a54af6ee0`
  - `upgrade_cap`: `0x925fcee37c48d15e07d1a86b70b64adac8dce157ed5a84369301c4a73e2f1ec4`
- Backlog item #1 archived: row removed from `project_change_opportunities.md`, recorded in new `project_change_opportunities_archive.md`, both indexed in `MEMORY.md`.
- `.claude/CLAUDE.md` "Current state" section updated to reflect the above.

### Open — must resolve

(none yet — no active Plan/Task has started)

### Exact next step

No plan or task is currently active. Backlog item #1 is complete; awaiting Frank's direction on the next opportunity (e.g. additional console commands for register/wrap/transfer/unwrap flows) or other work.
