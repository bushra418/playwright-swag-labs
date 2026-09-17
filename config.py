"""Test accounts, read from the environment.

These are Swag Labs' public demo credentials, so nothing here is secret. They
live in a module of their own rather than in conftest.py because importing a
conftest as a module is not something pytest promises. It works until the
rootdir or the import mode changes, and then fails somewhere that has nothing to
do with the test.
"""

import os

STANDARD_USER = os.environ.get("SWAG_USER", "standard_user")
STANDARD_PASS = os.environ.get("SWAG_PASS", "secret_sauce")
LOCKED_OUT_USER = os.environ.get("SWAG_LOCKED_USER", "locked_out_user")
