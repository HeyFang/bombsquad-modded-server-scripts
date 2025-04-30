# Released under the MIT License. See LICENSE for details.
#
"""Functionality related to net play."""
from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    pass


@dataclass
class HostInfo:
    """Info about a host."""
    build_number: int = 1232  # Non-default argument comes first
    name: str = "fangfingfong"  # Default argument comes after
    address: str | None = None  # Default argument
    port: int | None = None  # Default argument
