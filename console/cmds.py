#    Copyright Frank V. Castellucci
#    SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

"""Command handlers for the pysui-ct management console."""

import argparse
import datetime
import json
import pathlib
import re
import sys

import pysui.sui.sui_common.sui_commands as cmd
from pysui.abstracts.async_client import AsyncClientBase
import pysui.sui.sui_grpc.suimsgs.sui.rpc.v2 as sui_prot

PACKAGE: str | None = "0x2e2ff112f8752a7c7b05498039a431c8dbce1c57b7f6bdce270e759cb312aea1"
UPGRADE_CAP: str | None = "0x9e413bfa00d17e91691f06b1cdfeeef21bb5fe98287d09a85b685d7e39c5e5d5"
TOKEN_REGISTRY: str | None = "0xa0d715a3680e67b30fe2be480685fceefa377768106efbc7d6f1150559f2b194"
ACCOUNT_REGISTRY: str | None = "0x8d9a999bbbe9c82e2b0472f4476f7447de08ee3dd7fa8b856f9cf25201489aa4"
CONFIDENTIAL_TOKEN: str | None = "0x4fb12251b5003bb08efb6f78624bff5890a9692f21e868c94d10e40a7aa736a7"
POOL: str | None = "0x16088a0532db585c33e240712361f89731b0e2a362e1223d083e6250cb6baf91"
MANAGEMENT_CAP: str | None = "0x889ad267349c32146a38c7302206ea931e347892bbf6ce8b8eb4a8a1a7259cf2"

_PACKAGE_TYPE = "package"
_UPGRADE_CAP_TYPE = "::package::UpgradeCap"
_TOKEN_REGISTRY_FRAGMENT = "::contra::TokenRegistry"
_ACCOUNT_REGISTRY_FRAGMENT = "::contra::AccountRegistry"
_CONFIDENTIAL_TOKEN_FRAGMENT = "::contra::ConfidentialToken<"
_POOL_FRAGMENT = "::contra::Pool<"
_MANAGEMENT_CAP_FRAGMENT = "::contra::ManagementCap<"
_AUDITOR_KEY_ELEMENT_TYPE = "0x2::group_ops::Element<0x2::ristretto255::G>"


def _object_id_by_type_fragment(*, objects: list, type_fragment: str) -> str | None:
    """Find the first object id whose object_type contains the given fragment.

    :param objects: Objects returned in a transaction execution result
    :type objects: list
    :param type_fragment: A substring to match against each object's ``object_type``
    :type type_fragment: str
    :return: The matching object's id, or ``None`` if not found
    :rtype: str | None
    """
    for obj in objects:
        object_type = getattr(obj, "object_type", None) or ""
        if type_fragment in object_type:
            return getattr(obj, "object_id", None)
    return None


def _object_id_by_exact_type(*, objects: list, object_type: str) -> str | None:
    """Find the first object id whose object_type exactly equals the given value.

    :param objects: Objects returned in a transaction execution result
    :type objects: list
    :param object_type: The exact ``object_type`` string to match (e.g. ``"package"``)
    :type object_type: str
    :return: The matching object's id, or ``None`` if not found
    :rtype: str | None
    """
    for obj in objects:
        if getattr(obj, "object_type", None) == object_type:
            return getattr(obj, "object_id", None)
    return None


_CONSOLE_MODULE_PATH = pathlib.Path(__file__)


def _persist_defaults(*, values: dict[str, str | None]) -> None:
    """Rewrite this module's own source file, updating module-level default literals.

    Keeps ``console/cmds.py``'s hardcoded defaults in sync with the last successful
    devnet transaction, so the next console invocation starts from current ids
    instead of stale ones.

    :param values: Mapping of module-level constant name to its new value
    :type values: dict[str, str | None]
    """
    source = _CONSOLE_MODULE_PATH.read_text(encoding="utf-8")
    for name, value in values.items():
        literal = "None" if value is None else f'"{value}"'
        source = re.sub(
            rf"^{name}: str \| None = .*$",
            f"{name}: str | None = {literal}",
            source,
            count=1,
            flags=re.MULTILINE,
        )
    _CONSOLE_MODULE_PATH.write_text(source, encoding="utf-8")


async def publish(*, client: AsyncClientBase, args: argparse.Namespace) -> None:
    """Publish the contra Move package to devnet and record created object ids.

    The package's ``init`` function shares a ``TokenRegistry`` and an
    ``AccountRegistry`` in the same transaction, so both are captured here
    alongside the package id and upgrade cap.

    :param client: An active pysui async client
    :type client: AsyncClientBase
    :param args: Parsed arguments for the ``publish`` subcommand
    :type args: argparse.Namespace
    """
    global PACKAGE, UPGRADE_CAP, TOKEN_REGISTRY, ACCOUNT_REGISTRY  # pylint: disable=global-statement

    active_address = client.config.active_address  # type: ignore

    try:
        txn = await client.transaction(initial_sender=active_address)
        upc = await txn.publish(project_path=args.package)
        await txn.transfer_objects(transfers=[upc], recipient=active_address)
        txdict = await txn.build_and_sign(
            gas_budget=args.budget,
            use_gas_objects=[args.gas] if args.gas else None,
        )
        result = await client.execute(command=cmd.ExecuteTransaction(**txdict))
    except RuntimeError as exc:
        print(exc.args, file=sys.stderr)
        return

    if not result.is_ok():
        print(result.result_string, file=sys.stderr)
        return

    tx_result: sui_prot.ExecutedTransaction = result.result_data

    if not tx_result.effects.status.success:  # type: ignore
        print("Transaction failed", file=sys.stderr)
        return

    objects = tx_result.effects.changed_objects  # type: ignore

    PACKAGE = _object_id_by_exact_type(objects=objects, object_type=_PACKAGE_TYPE)
    UPGRADE_CAP = _object_id_by_type_fragment(objects=objects, type_fragment=_UPGRADE_CAP_TYPE)
    TOKEN_REGISTRY = _object_id_by_type_fragment(objects=objects, type_fragment=_TOKEN_REGISTRY_FRAGMENT)
    ACCOUNT_REGISTRY = _object_id_by_type_fragment(objects=objects, type_fragment=_ACCOUNT_REGISTRY_FRAGMENT)

    found = {
        "PACKAGE": PACKAGE,
        "UPGRADE_CAP": UPGRADE_CAP,
        "TOKEN_REGISTRY": TOKEN_REGISTRY,
        "ACCOUNT_REGISTRY": ACCOUNT_REGISTRY,
    }
    _persist_defaults(values=found)
    for name, value in found.items():
        status = value if value else "NOT FOUND"
        print(f"{name.lower()}: {status}")


async def create_ct_token(*, client: AsyncClientBase, args: argparse.Namespace) -> None:
    """Create and share a ConfidentialToken<T> for a token type, using its TreasuryCap.

    The TreasuryCap<T> and token type belong to the token's issuing package, not this
    project, so both are supplied by the caller. On success, the resulting
    ManagementCap<T> is transferred to the active address and the created
    ConfidentialToken<T>, Pool<T>, and ManagementCap<T> object ids are recorded.

    :param client: An active pysui async client
    :type client: AsyncClientBase
    :param args: Parsed arguments for the ``create-ct-token`` subcommand
    :type args: argparse.Namespace
    """
    global CONFIDENTIAL_TOKEN, POOL, MANAGEMENT_CAP  # pylint: disable=global-statement

    if PACKAGE is None or TOKEN_REGISTRY is None:
        print(
            "PACKAGE and TOKEN_REGISTRY must be set before creating a confidential token.",
            file=sys.stderr,
        )
        return

    active_address = client.config.active_address  # type: ignore

    try:
        txn = await client.transaction(initial_sender=active_address)
        auditor_public_keys = await txn.make_move_vector(
            items=[], item_type=_AUDITOR_KEY_ELEMENT_TYPE
        )
        ct, management_cap = await txn.move_call(
            target=f"{PACKAGE}::contra::new_confidential_token",
            arguments=[TOKEN_REGISTRY, args.treasury_cap, auditor_public_keys],
            type_arguments=[args.token_type],
        )
        await txn.move_call(
            target=f"{PACKAGE}::contra::share_confidential_token",
            arguments=[ct],
            type_arguments=[args.token_type],
        )
        await txn.transfer_objects(transfers=[management_cap], recipient=active_address)
        txdict = await txn.build_and_sign(
            gas_budget=args.budget,
            use_gas_objects=[args.gas] if args.gas else None,
        )
        result = await client.execute(command=cmd.ExecuteTransaction(**txdict))
    except RuntimeError as exc:
        print(exc.args, file=sys.stderr)
        return

    if not result.is_ok():
        print(result.result_string, file=sys.stderr)
        return

    tx_result: sui_prot.ExecutedTransaction = result.result_data

    if not tx_result.effects.status.success:  # type: ignore
        print("Transaction failed", file=sys.stderr)
        return

    objects = tx_result.effects.changed_objects  # type: ignore

    CONFIDENTIAL_TOKEN = _object_id_by_type_fragment(
        objects=objects, type_fragment=_CONFIDENTIAL_TOKEN_FRAGMENT
    )
    POOL = _object_id_by_type_fragment(objects=objects, type_fragment=_POOL_FRAGMENT)
    MANAGEMENT_CAP = _object_id_by_type_fragment(
        objects=objects, type_fragment=_MANAGEMENT_CAP_FRAGMENT
    )

    found = {
        "CONFIDENTIAL_TOKEN": CONFIDENTIAL_TOKEN,
        "POOL": POOL,
        "MANAGEMENT_CAP": MANAGEMENT_CAP,
    }
    _persist_defaults(values=found)
    for name, value in found.items():
        status = value if value else "NOT FOUND"
        print(f"{name.lower()}: {status}")


async def export_ids(*, client: AsyncClientBase, args: argparse.Namespace) -> None:
    """Export the currently captured object ids to a JSON file under ``~/.pysui``.

    Writes ``package_id``, ``upgrade_cap``, ``token_registry``, ``account_registry``,
    ``confidential_token``, ``pool``, and ``management_cap`` from this module's current
    state to ``~/.pysui/pysui_ct_<YYYY-MM-DD>.json``.

    :param client: An active pysui async client (unused, kept for dispatch signature parity)
    :type client: AsyncClientBase
    :param args: Parsed arguments for the ``export-ids`` subcommand
    :type args: argparse.Namespace
    """
    ids = {
        "package_id": PACKAGE,
        "upgrade_cap": UPGRADE_CAP,
        "token_registry": TOKEN_REGISTRY,
        "account_registry": ACCOUNT_REGISTRY,
        "confidential_token": CONFIDENTIAL_TOKEN,
        "pool": POOL,
        "management_cap": MANAGEMENT_CAP,
    }

    output_dir = pathlib.Path.home() / ".pysui"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"pysui_ct_{datetime.date.today().isoformat()}.json"
    output_path.write_text(json.dumps(ids, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {output_path}")


CONSOLE_CMD_DISPATCH = {
    "publish": publish,
    "create-ct-token": create_ct_token,
    "export-ids": export_ids,
}
