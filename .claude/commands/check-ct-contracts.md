Check whether the vendored CT Move contracts in `pysui-ct/contracts/sources/` have drifted
from upstream `~/mysten_repos/confidential-transfers`.

## Step 1 — Load baseline

Read `~/frankc01/pysui-ct/.claude/ct-baseline.json` for the baseline commit, tracked paths, and
vendored-state notes.

## Step 2 — Check upstream

1. Run: `git -C ~/mysten_repos/confidential-transfers pull`
2. Run: `git -C ~/mysten_repos/confidential-transfers log <baseline_commit>..HEAD --oneline -- <tracked_paths>`
3. If commits exist affecting tracked paths, run: `git -C ~/mysten_repos/confidential-transfers diff <baseline_commit>..HEAD -- <tracked_paths>`
4. Also run `diff -rq --exclude='.DS_Store' ~/mysten_repos/confidential-transfers/move/sources/ ~/frankc01/pysui-ct/contracts/sources/` to catch drift against what is actually vendored locally, independent of `baseline_commit` — the vendored copy is a hand-merged composite from two partial copy passes, not synced to any single commit, so this file-level check against the LOCAL copy matters as much as the commit-range diff.

## Step 3 — Analyze impact

Read the changed `.move` files' diff content plus `~/frankc01/pysui-ct/console/cmds.py` and
`~/frankc01/pysui-ct/contracts/sources/`. For each changed struct/function, state:
- Whether it is used by pysui-ct's 9 validated use cases (register, merge, transfer,
  batched_transfer, wrap, unwrap, set_public_key) or by `console/cmds.py`.
- Whether the vendored local copy needs updating, and why.

Be specific about function/struct names — do not summarize at the file level only.

## Step 4 — Report

Output a concise report with these sections:
- **Move contracts (vs. baseline_commit)** — unchanged / changed. If changed: list affected
  files, summarize what changed structurally (types removed/added, signature changes), and
  whether pysui-ct's vendored copy needs updating and why.
- **Local vendored copy (vs. current upstream)** — list every file that differs, per Step 2.4's
  `diff -rq`, independent of `baseline_commit`.
- **Recommended actions** — numbered list of concrete steps, or "Nothing to do — vendored copy
  current."

Do NOT copy any files over the local `contracts/sources/` copy — this project vendors Move
contracts manually only, per project convention. Flag differences for Frank to review and copy
by hand if he chooses.

## Step 5 — Offer baseline update

If upstream HEAD has advanced but the vendored copy is confirmed current (or Frank confirms he
has reviewed and accepted the changes), offer to update `baseline_commit` and `baseline_date`
in `.claude/ct-baseline.json` to the current upstream HEAD. Wait for Frank's explicit approval
before writing.
