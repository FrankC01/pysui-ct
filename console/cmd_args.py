#    Copyright Frank V. Castellucci
#    SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

"""Argument parser construction for the pysui-ct management console."""

import argparse


def build_parser(*, argv: list[str]) -> argparse.Namespace:
    """Build and parse command line arguments for the console.

    :param argv: Command line argument list (excluding program name)
    :type argv: list[str]
    :return: Parsed arguments, including the resolved ``subcommand`` attribute
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        prog="console", description="pysui-ct management console"
    )
    subparser = parser.add_subparsers(title="commands", dest="subcommand")

    publish_parser = subparser.add_parser(
        "publish", help="Publish the contra (Confidential Transfer) Move package to devnet."
    )
    publish_parser.add_argument(
        "-p",
        "--package",
        required=True,
        help="Path to the Move package folder to publish.",
    )
    publish_parser.add_argument(
        "-g",
        "--gas",
        required=False,
        default=None,
        help="Gas object ID to pay the transaction from. Optional.",
    )
    publish_parser.add_argument(
        "-b",
        "--budget",
        required=False,
        default=None,
        type=str,
        help="Transaction gas budget. Optional.",
    )
    publish_parser.set_defaults(subcommand="publish")

    create_ct_token_parser = subparser.add_parser(
        "create-ct-token",
        help="Create and share a ConfidentialToken<T> for a token type, using its TreasuryCap.",
    )
    create_ct_token_parser.add_argument(
        "-t",
        "--treasury-cap",
        required=True,
        type=str,
        help="TreasuryCap<T> object id for the token type, owned by the token's issuing package.",
    )
    create_ct_token_parser.add_argument(
        "-y",
        "--token-type",
        required=True,
        type=str,
        help="Fully qualified coin type T (e.g. 0x...::pysui_token::PYSUI_TOKEN).",
    )
    create_ct_token_parser.add_argument(
        "-g",
        "--gas",
        required=False,
        default=None,
        help="Gas object ID to pay the transaction from. Optional.",
    )
    create_ct_token_parser.add_argument(
        "-b",
        "--budget",
        required=False,
        default=None,
        type=str,
        help="Transaction gas budget. Optional.",
    )
    create_ct_token_parser.set_defaults(subcommand="create-ct-token")

    export_ids_parser = subparser.add_parser(
        "export-ids",
        help="Export captured object ids to ~/.pysui/pysui_ct_<date>.json.",
    )
    export_ids_parser.set_defaults(subcommand="export-ids")

    return parser.parse_args(argv)
