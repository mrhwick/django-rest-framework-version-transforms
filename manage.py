#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from tests.conftest import pytest_configure

if __name__ == "__main__":

    pytest_configure()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
