import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Sequence

import git
from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import (
    ClientCapabilities,
    ListRootsResult,
    RootsCapability,
    TextContent,
    Tool,
)
