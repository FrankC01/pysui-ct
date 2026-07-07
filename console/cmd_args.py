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

    return parser.parse_args(argv)
