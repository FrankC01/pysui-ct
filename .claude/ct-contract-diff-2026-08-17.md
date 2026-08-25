# CT Move Contract Diff — 2026-08-17

> **SUPERSEDED / STALE as of 2026-08-23.** The auditor-model bullet below has the direction
> backwards (it claims per-account escrow was newly *added*; a rigorous baseline-tracked
> re-check proved escrow was actually already present at baseline and was *removed*). More
> importantly, `contracts/sources/` was fully resynced to upstream `c2f842c` on 2026-08-23, so
> this entire diff (against the much older `96f9c27`) no longer reflects the gap between
> vendored and upstream — there currently is no gap. See project memory
> `project_ct_contract_api_refresh_2026_07` (2026-08-23 section) for the corrected, verified
> record. Kept here for historical audit trail only — do not hand-copy from this file.

Source: `check-ct-contracts` skill run. Upstream `~/mysten_repos/confidential-transfers`
pulled (`257f9a0..96f9c27`) and diffed against vendored copy in
`~/frankc01/pysui-ct/contracts/sources/`. No files copied — vendoring stays manual per
project convention.

All 9 shared `*.move` files differ from upstream. `deny_list.move` (10th vendored file)
is unchanged. No files missing locally; no new files upstream.

## Per-file changes

### auditors.move
- Auditing model flipped from per-transfer to per-account.
- `AuditorPackage`, `VerifiedAuditorHandles` removed.
- `KeyEncryption`, `VerifiedKeyEncryption` added.
- `Auditors` struct restructured: `(current_pks, previous_pks)` → `(pks, version,
  recommended_min_version)`; pk type now `vector<Element<G>>` instead of
  `vector<PublicKey>`.
- Removed: `new_auditor_package`, `verify_transfer`, `next`, `destroy`.
- Added: `verify_key_encryption`, `verify_key_encryption_for_testing`, accessors
  `pks()`, `is_empty()`, `version()`, `recommended_min_version()`, `ciphertext()`,
  `key_version()`, `is_set()`.
- **Breaking: YES** — struct and function set incompatible with prior version.

### balance.move
- All `PublicKey`-typed params → `Element<G>`: `merge_encrypted`,
  `try_split_to_public`, `try_split_batch`, `try_update`, `try_set_public_key`.
- Added: `max_upper_bound_minus_1()`.
- No struct changes, no removals.
- **Breaking: YES** — param type change on public functions.

### contra.move (heaviest impact)
- `Account.default_pk: Option<PublicKey>` field removed (permissionless registration
  disabled).
- `TokenAccount<T>.pk` → `Element<G>`; added `verified_key_encryption` field.
- `TransferBatch::Ok` — removed `auditor_data` field.
- Removed: `set_default_pk_as_sender`, `set_default_pk_as_object`,
  `register_with_default_pk`, `try_register_with_default_pk`,
  `rekey_token_account`, `try_rekey_token_account_and_unpause`.
- Signature changes:
  - `register<T>(account, auth, pk)` → `register<T>(account, auth, ct, pk,
    key_encryption)`.
  - `batched_transfer` — `auditor_package: Option<AuditorPackage>` param removed;
    `auditor_pks` removed from receiver list.
  - `update_auditors<T>(ct, cap, current_pks, previous_pks)` →
    `update_auditors<T>(ct, cap, public_keys, bump_recommended_min)`.
- Added: `set_public_key<T>`, `try_set_public_key_and_unpause<T>`.
- Constants: removed `EReceiverNotRegistered`, `ERegistrationNotPermissionless`,
  `EDefaultPkNotSet`, `DST_AUDITOR_ELGAMAL`; added `EIdentityPublicKey`,
  `DST_KEY_CONSISTENCY`, `DST_RANGE_PROOF_32`.
- **Breaking: SEVERE** — register/batched_transfer/update_auditors all incompatible;
  default-key and per-transfer auditor model gone entirely.

### events.move
- `NewRegistrationEvent<T>.pk` → `Element<G>`; added `verified_key_encryption`.
- Removed: `DefaultPkRotatedEvent`, `TokenRekeyedEvent<T>`,
  `TryTokenRekeyFailedEvent<T>`.
- Added: `UpdatedPublicKeyEvent<T>` (replaces TokenRekeyedEvent, generic, includes
  `verified_key_encryption`).
- `TransferEvent<T>` — `sender_pk`/`receiver_pk` now `Element<G>`; removed
  `auditor_decryption_handles`, `auditor_pk`.
- `UpdateAuditorsEvent<T>` fields: `(current_pks, previous_pks)` →
  `(public_keys, version, recommended_min_version)`.
- Added functions: `emit_try_set_public_key_failed()`, `emit_updated_public_key<T>`.
- Removed functions: `emit_default_pk_rotated`, `emit_token_rekeyed`,
  `emit_try_token_rekey_failed`.
- **Breaking: YES** — event shapes incompatible; auditor fields dropped from
  TransferEvent.

### nizk.move
- Added `KeyConsistencyProof` struct (proves viewing-key limbs encrypt the same
  scalar sum to all auditors; 8 limbs × m recipients).
- Added: `verify_key_consistency()`, `prove_key_consistency()` (test-only),
  `scalar_to_limbs()` (test-only), `handle_eq_proof_for_testing()` (test-only).
- `verify_elgamal()` param changed: `pk: &PublicKey` → `pk: &Element<G>`.
- Constants added: `KEY_CONSISTENCY_LIMBS = 8`, `EMalformedKeyConsistencyProof`.
- No removal of core proof functions (`DdhProof`/`ConsistencyProof` from the
  2026-07-16 refresh untouched here).
- **Breaking: MODERATE** — `verify_elgamal` param type change; new proof type
  callers may need to construct.

### policy.move
- Removed: `is_permissionless()`.
- No struct/other signature changes.
- **Breaking: MINOR** — callers relying on `is_permissionless()` must inline the
  bitmap check.

### twisted_elgamal.move
- `PublicKey` struct removed entirely (was a wrapper over `Element<G>` with an
  identity check).
- Removed: `public_key()` (constructor), `as_element()` (accessor).
- Added: `MultiRecipientEncryption` struct (shared ciphertext + per-recipient
  decryption handles, for auditor reads), `new_multi_recipient_encryption()`,
  `multi_recipient_ciphertext()`, `multi_recipient_decryption_handles()` (+ use fun
  aliases), `add_assign()`, `shift_left()`, `ciphertext_for_testing()` (test-only).
- **Breaking: YES** — `PublicKey` type and constructors gone; callers work with raw
  `Element<G>` and check identity separately.

### decode.move / encrypted_amount.move
- Both flagged as differing in the Step 2 diff (`decode.move`, `encrypted_amount.move`)
  but were not separately itemized in this pass — the summarizing agent's report
  covered the other 7 files in detail but omitted these two. Detailed field-level
  changes (decode byte-layouts, encrypted_amount struct/function changes) need to be
  captured when doing the actual hand-copy — do not assume "no changes" from their
  absence above.

## Overall breaking-change summary

**Severity: HIGH.** This is a paradigm shift, not an incremental refresh:

1. **Type system** — `PublicKey` type removed project-wide; all key params now
   `Element<G>`.
2. **Auditor model** — per-transfer → per-account. `AuditorPackage` /
   `VerifiedAuditorHandles` gone; `KeyEncryption` / `VerifiedKeyEncryption` /
   `MultiRecipientEncryption` / `KeyConsistencyProof` added.
3. **Registration** — `register()` signature incompatible; default-key pattern
   removed entirely.
4. **Transfer** — `batched_transfer()` no longer takes auditor data;
   `TransferEvent` lost auditor fields.
5. **Key rotation** — `rekey_token_account()` removed; replaced by
   `set_public_key()` / `try_set_public_key_and_unpause()` with different
   signature/logic.
6. **Policy** — `is_permissionless()` removed.
7. **Events** — `DefaultPkRotatedEvent`, `TokenRekeyedEvent`,
   `TryTokenRekeyFailedEvent` removed; `UpdatedPublicKeyEvent` added;
   `UpdateAuditorsEvent` fields changed.
8. **Account structure** — `Account.default_pk` removed;
   `TokenAccount.verified_key_encryption` added.

**pysui #79 impact:** entry-function signatures for `register()`,
`batched_transfer()`, `set_public_key()`/`update_auditors()` are all incompatible
with the currently-integrated 9-use-case surface. Event decoding must handle new
auditor-related fields. `Element<G>` replaces `PublicKey` in serialization —
`pysui-crypto` alignment needs re-checking (as with the 2026-07-16 refresh, see
[[project-ct-contract-api-refresh-2026-07]]).

No files copied. Copying and republish to devnet is tracked as backlog item
"Update move contracts."
