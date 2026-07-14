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

### Task 2 completed (2026-07-08) — CT Move contract drift check command
- Created `.claude/commands/check-ct-contracts.md` — pulls `~/mysten_repos/confidential-transfers` and diffs its `move/sources/*.move` files against this project's vendored `contracts/sources/`, and reports differences. Does not auto-copy; Move contracts in this project are vendored manually per project convention.

### Task 3 completed (2026-07-08) — Synced contra.move with upstream MAX_BATCH_RECIPIENTS fix
- Ran `/check-ct-contracts`: pulled `~/mysten_repos/confidential-transfers` (fast-forward `17523de..aaac43e`), diffed against `contracts/sources/`. Only `contra.move` differed; all other 9 vendored modules matched exactly.
- Upstream fix: adds an explicit `MAX_BATCH_RECIPIENTS: u64 = 255` cap on batched-transfer recipients, a new `EBatchTooLarge: u64 = 12` error code, and an `assert!` enforcing the cap in the batch-transfer function. The bound exists so the `u8` receiver index (`next_index`) can't overflow.
- Cross-checked via the same upstream pull's ts-sdk diff: the TS SDK's own `MAX_BATCH_RECIPIENTS` was previously **7** (an artifact of the Bulletproof aggregate range-proof verifier's 8-proof-per-call limit: 7 recipients + 1 sender), now raised to 255 to match the Move-side fix. The e2e test (`core_flow.test.ts`) was rewritten to exercise 11 recipients (was 2) specifically to prove batch indices run past the old 7-cap.
- Frank approved bringing the fix into this repo's vendored copy; applied manually to `contracts/sources/contra.move` (new error code, new constant, new assert in the batch-transfer function). Verified byte-for-byte match against upstream via `diff -u`.
- Decision (Frank): pysui's own `batched_transfer` client support will not impose a client-side recipient cap at 7, in anticipation of this fix.
- **Gotcha:** the devnet-published `contra` package (`package_id` `0xdbf5...`) now has stale on-chain bytecode relative to local source — this fix is not live on-chain until republished. Republishing was explicitly deferred by Frank to a later session.

### Open — must resolve

- Republish `contra` package to devnet to pick up the `MAX_BATCH_RECIPIENTS` fix in `contra.move` (deferred by Frank on 2026-07-08). Republishing will change `package_id` (and possibly `upgrade_cap`); `console/cmds.py` module-level ID defaults and any downstream consumers (pysui #79's `PrivateFundsConfig`) will need updating once republished.

### Exact next step

No plan or task is currently active. Local `contracts/sources/contra.move` is now one fix ahead of the published devnet package (`MAX_BATCH_RECIPIENTS` widened 7→255, not yet republished — see "Open — must resolve"). Awaiting Frank's direction: republish `contra` to devnet, or move on to other work (e.g. additional console commands for register/wrap/transfer/unwrap flows).

### Task 4 completed (2026-07-14) — Republish contra + create-ct-token / export-ids console commands

- Devnet was found wiped clean as of 2026-07-13/14 (separate from the `MAX_BATCH_RECIPIENTS` staleness noted in Task 3) — all previously published `contra` objects no longer existed on-chain. Captured as project memory `project_devnet_weekly_wipe` (devnet resets on a weekly cadence; republish before assuming any captured id is live).
- Republished `contra` to devnet, picking up the `MAX_BATCH_RECIPIENTS` fix from Task 3. This resolves Task 3's "Open — must resolve" item. New ids:
  - `package_id`: `0x2e2ff112f8752a7c7b05498039a431c8dbce1c57b7f6bdce270e759cb312aea1`
  - `token_registry`: `0xa0d715a3680e67b30fe2be480685fceefa377768106efbc7d6f1150559f2b194`
  - `account_registry`: `0x8d9a999bbbe9c82e2b0472f4476f7447de08ee3dd7fa8b856f9cf25201489aa4`
  - `upgrade_cap`: `0x9e413bfa00d17e91691f06b1cdfeeef21bb5fe98287d09a85b685d7e39c5e5d5`
  - `.claude/CLAUDE.md` "Current state" section updated with these values.
- Added a `create-ct-token` subcommand to `console/cmds.py`/`cmd_args.py`: calls `contra::new_confidential_token<T>` (using a caller-supplied `TreasuryCap<T>` and token type, plus an empty auditor-keys vector built via `txn.make_move_vector`), then `contra::share_confidential_token<T>`, then transfers the resulting `ManagementCap<T>` to the active address, all in one PTB.
- Ran `create-ct-token` against `PYSUI_TOKEN` (using `pysui-token`'s freshly republished `TreasuryCap` `0x028956f3640964cd5b402863e441690399358488cbbf27db8b61ad816a945ad9` and package `0x9ba6ae824a3d9b281041d0b0d1f4b407121669ea84a11cfea3b3d390b4a8c10d`). Verified all three resulting objects via `wallet object` dumps:
  - `confidential_token`: `0x4fb12251b5003bb08efb6f78624bff5890a9692f21e868c94d10e40a7aa736a7` (shared, `policy: null`, `auditors.pks: []`)
  - `pool`: `0x16088a0532db585c33e240712361f89731b0e2a362e1223d083e6250cb6baf91` (shared)
  - `management_cap`: `0x889ad267349c32146a38c7302206ea931e347892bbf6ce8b8eb4a8a1a7259cf2` (owned by active address)
- Closed a gap Frank flagged: neither `publish()` nor `create_ct_token()` originally wrote captured ids back into `cmds.py`'s hardcoded module-level defaults — they only set in-process globals and printed. Added a `_persist_defaults()` helper that regex-rewrites `cmds.py`'s own source file with the new literals; both commands now call it on success.
- Added a reusable `export-ids` subcommand that writes `package_id`, `upgrade_cap`, `token_registry`, `account_registry`, `confidential_token`, `pool`, `management_cap` to `~/.pysui/pysui_ct_<YYYY-MM-DD>.json`. Ran once, producing `~/.pysui/pysui_ct_2026-07-14.json`.
- Discussed (no implementation): setting a `Policy` on `ConfidentialToken<T>` requires a companion Move module holding a witness type and its own `auth_X<T>()` entry functions that call `contra::authorize_with_witness` — out of scope for now since it would block the permissionless register/wrap/unwrap flows still to be tested.

### Open — none

No open items currently. Next natural step: console commands for register/wrap/transfer/unwrap flows against the live `ConfidentialToken<PYSUI_TOKEN>`.
