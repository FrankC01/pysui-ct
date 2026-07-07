#    Copyright Frank V. Castellucci
#    SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

"""Command handlers for the pysui-ct management console."""

import argparse
import sys

import pysui.sui.sui_common.sui_commands as cmd
from pysui.abstracts.async_client import AsyncClientBase
import pysui.sui.sui_grpc.suimsgs.sui.rpc.v2 as sui_prot

PACKAGE: str | None = "0xdbf579054d6a93d3eca02d549cf16d4008475c8930fdfda40bef763a7385fff1"
UPGRADE_CAP: str | None = "0x925fcee37c48d15e07d1a86b70b64adac8dce157ed5a84369301c4a73e2f1ec4"
TOKEN_REGISTRY: str | None = "0x5fde83596901ff336e065e63b9212a3ff066a6b74a3c0ce2f4af3708df636638"
ACCOUNT_REGISTRY: str | None = "0xebf3a594bd19565ff273bd99251e8ca33469b178eb45c0a9acaccf7a54af6ee0"

_PACKAGE_TYPE = "package"
_UPGRADE_CAP_TYPE = "::package::UpgradeCap"
_TOKEN_REGISTRY_FRAGMENT = "::contra::TokenRegistry"
_ACCOUNT_REGISTRY_FRAGMENT = "::contra::AccountRegistry"


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
        "package": PACKAGE,
        "upgrade_cap": UPGRADE_CAP,
        "token_registry": TOKEN_REGISTRY,
        "account_registry": ACCOUNT_REGISTRY,
    }
    for name, value in found.items():
        status = value if value else "NOT FOUND"
        print(f"{name}: {status}")


CONSOLE_CMD_DISPATCH = {"publish": publish}
