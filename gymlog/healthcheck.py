#!/usr/bin/env python3

import sys
from urllib.request import urlopen
from urllib.error import URLError

if __name__ == "__main__":
    try:
        r = urlopen("http://127.0.0.1:5000")
        if r.getcode() == 200:
            sys.exit(0)
        else:
            sys.exit(1)
    except URLError:
        sys.exit(1)

