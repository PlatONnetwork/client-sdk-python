from __future__ import absolute_import

import pkg_resources
import warnings
import sys

from alaya.packages.platon_keyfile.keyfile import (  # noqa: F401
    load_keyfile,
    create_keyfile_json,
    decode_keyfile_json,
    extract_key_from_keyfile,
)


if sys.version_info.major < 3:
    warnings.simplefilter('always', DeprecationWarning)
    warnings.warn(DeprecationWarning(
        "The `platon-keyfile` library is dropping support for Python 2.  Upgrade to Python 3."
    ))
    warnings.resetwarnings()


# __version__ = pkg_resources.get_distribution("platon-keyfile").version
