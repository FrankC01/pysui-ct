---
model: haiku
---

Perform the following steps in order and report results for each.

## Step 1 — Pull the Mysten confidential-transfers repo

Run `git -C ~/mysten_repos/confidential-transfers pull` and report success or failure and any relevant output.

## Step 2 — Diff Move source files

Run `diff -rq --exclude='.DS_Store' ~/mysten_repos/confidential-transfers/move/sources/ ~/frankc01/pysui-ct/contracts/sources/` to compare the upstream Move contract sources against this project's vendored copy.

## Step 3 — Report diff findings

Report exactly what Step 2 found: list every `*.move` file that differs, is missing locally, or is new upstream. If there were no differences, say so explicitly.

Do NOT copy any files over the local `contracts/sources/` copy — this project vendors Move contracts manually only, per project convention. Flag differences for Frank to review and copy by hand if he chooses.
