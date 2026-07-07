#    Copyright Frank V. Castellucci
#    SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

"""Entry point for the pysui-ct management console."""

import asyncio
import sys

from pysui import PysuiConfiguration
from pysui.sui.sui_common.factory import client_factory

from console.cmd_args import build_parser
from console.cmds import CONSOLE_CMD_DISPATCH


async def _run(*, argv: list[str]) -> None:
    """Parse arguments, dispatch to the matching command handler, and clean up.

    :param argv: Command line argument list (excluding program name)
    :type argv: list[str]
    """
    args = build_parser(argv=argv)
    handler = CONSOLE_CMD_DISPATCH.get(args.subcommand)
    if handler is None:
        print(f"Unable to resolve function for {args.subcommand}", file=sys.stderr)
        return

    cfg = PysuiConfiguration()
    client = client_factory(pysui_config=cfg)
    try:
        await handler(client=client, args=args)
    finally:
        await client.close()  # type: ignore


def main() -> None:
    """Synchronous entry point for the console."""
    asyncio.run(_run(argv=sys.argv[1:]))


if __name__ == "__main__":
    main()
