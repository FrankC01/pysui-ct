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
- `package_id`: `0x2e2ff112f8752a7c7b05498039a431c8dbce1c57b7f6bdce270e759cb312aea1`
- `token_registry`: `0xa0d715a3680e67b30fe2be480685fceefa377768106efbc7d6f1150559f2b194`
- `account_registry`: `0x8d9a999bbbe9c82e2b0472f4476f7447de08ee3dd7fa8b856f9cf25201489aa4`
- `upgrade_cap`: `0x9e413bfa00d17e91691f06b1cdfeeef21bb5fe98287d09a85b685d7e39c5e5d5`

Devnet is wiped on a weekly cadence by Mysten, which invalidates these ids — republish before
assuming any of them are live (see project memory `project_devnet_weekly_wipe`).

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
