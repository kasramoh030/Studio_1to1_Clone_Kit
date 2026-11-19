#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-command shortcut for `/home/user/animation-studio/tools/chat_workspace_migrator.py`."""
import os
import sys

TOOL = "/home/user/animation-studio/tools/chat_workspace_migrator.py"
os.execv(sys.executable, [sys.executable, TOOL, *sys.argv[1:]])
