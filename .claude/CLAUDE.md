# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`pysui-ct` vendors Mysten Labs' Confidential Transfer (CT) Move contracts onto **devnet**,
plus a management CLI for CT policies/objects, so that pysui #79's Private Funds
(Confidential Transfer) client work can develop and test against real CT semantics before
Mysten deploys CT to a public network (targeted ~Aug/Sept 2026).

This repo is the **middle tier** of a three-tier chain:

```
pysui-token (leaf, DONE) -> pysui-ct (THIS repo) -> pysui #79 (id consumer)
```

- **pysui-token** (sibling repo, complete): publishes the `pysui_token` coin. Coin type
  `0xb0eaf410ca6c030f450fb0ab96e497c6007c7284f688674e78aedd1c495bd760::pysui_token::PYSUI_TOKEN`
  is live on devnet with minted test balances.
- **pysui-ct** (here): vendors Mysten's CT Move contracts, deploys to devnet, wraps/deposits
  `PYSUI_TOKEN` balances into CT objects, and exposes a management CLI for CT policies/objects —
  covering the 9 use cases already validated against Move contracts in pysui #79 Phases 1–3
  (register, merge, transfer, batched_transfer, wrap, unwrap, set_public_key).
- **pysui #79** (downstream client, in the `pysui` repo): consumes this project's published CT
  package ID and CT object IDs to replace Ben Riva's placeholder `0x` addresses in
  `PrivateFundsConfig`.

### Boundary — read before touching anything upstream/downstream

This project owns nothing in `pysui-token` or `pysui #79`. Its only public output — the exact
fields required by pysui #79's `PrivateFundsGroup` (`pysui/private_transfer/config.py`):

- `package_id` — the published Confidential Transfer package id for this network
- `token_registry` — the `TokenRegistry` shared-object id for this network
- `account_registry` — the `AccountRegistry` shared-object id for this network

These three values replace Ben Riva's placeholder `0x` entries in `PrivateFundsConfig.json`.
Data/IDs flow **one way, out of this repo**.

## Current state

First backlog item complete. `contracts/` holds the vendored Mysten Confidential Transfer Move
package (module `contra::contra`, 10 source files: contra, policy, balance, encrypted_amount,
twisted_elgamal, nizk, auditors, deny_list, decode, events). `console/` is a scaffolded
pysui-driven CLI (`__init__.py`, `__main__.py`, `cmd_args.py`, `cmds.py`) mirroring
`pysui-token/console/`'s layout, currently exposing a `publish` subcommand.

The `contra` package has been published to devnet. `console/cmds.py` holds the captured ids as
module-level defaults:
- `package_id`: `0xdbf579054d6a93d3eca02d549cf16d4008475c8930fdfda40bef763a7385fff1`
- `token_registry`: `0x5fde83596901ff336e065e63b9212a3ff066a6b74a3c0ce2f4af3708df636638`
- `account_registry`: `0xebf3a594bd19565ff273bd99251e8ca33469b178eb45c0a9acaccf7a54af6ee0`
- `upgrade_cap`: `0x925fcee37c48d15e07d1a86b70b64adac8dce157ed5a84369301c4a73e2f1ec4`

These are the three values pysui #79's `PrivateFundsConfig` needs (package_id, token_registry,
account_registry). No commits yet.

## Design decisions locked so far

- **Repo name and location**: `pysui-ct`, sibling to `pysui-token` (i.e. `~/frankc01/pysui-ct`).
- **Management CLI**: pysui-driven (dogfooded, following pysui-token's precedent), running in
  a dedicated virtual environment pinned to **pysui 1.1.0**. Must be UCI compliant. Framing
  structure to reuse: `~/frankc01/pysui-token/console/` (the Python management console pattern
  from the pysui-token project).
- **Move contracts**: Frank copies the actual Mysten CT Move contracts into `pysui-ct`
  manually — not sourced via automated vendoring or agent-driven lookup.
- **Network**: devnet. The default `PysuiConfiguration` already has devnet as its active
  profile, consistent with pysui-token and Plan #79.

## Backlog

Backlog file: `~/.claude/projects/-Users-fastfrank-frankc01-pysui-ct/memory/project_change_opportunities.md`

## Code conventions

All generated code in this project follows the global Claude Code conventions established in
`~/.claude/CLAUDE.md` (originating from pysui Plan #79, 2026-07-05) — apply from the start,
not retrofitted later:

- Keyword arguments only for new methods/functions — no positional-only parameter lists.
- No `Any` type hints — every type hint is a concrete type or well-defined abstraction, unless
  there is a hard, explicitly justified exception.
- Docstrings on everything — modules, classes, methods, functions.
- Copyright header on every new source file, placed before the module docstring:
  ```
  #    Copyright Frank V. Castellucci
  #    SPDX-License-Identifier: Apache-2.0

  # -*- coding: utf-8 -*-
  ```

## References

- Plan #79 handoff: `~/frankc01/pysui/.claude/session-handoff-plan79-private-funds.md`
- pysui-token seed brief (structural template): `~/frankc01/pysui-token/.claude/CLAUDE.md`
- Mysten CT contacts: Ben Riva (CT Move contract + can supply deployed test object addresses),
  Joy Zhang (fastcrypto/pysui-crypto CT crypto) — pysui memory
  `reference_mysten_ct_contacts.md`
