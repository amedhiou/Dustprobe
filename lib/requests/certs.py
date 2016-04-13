#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
certs.py
~~~~~~~~

This module returns the preferred default CA certificate bundle.

If you are packaging Requests, e.g., for a Linux distribution or a managed
environment, you can change the definition of where() to return a separately
packaged CA bundle.
"""
import os.path

try:
    from certifi import where
except ImportError:
    def where():
        """Return the preferred certificate bundle."""
        # vendored bundle inside Requests
        return "/etc/ssl/certs/ca-certificates.crt"

if __name__ == '__main__':
    print(where())