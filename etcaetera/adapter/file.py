import os
import imp

from .base import Adapter
from ..utils import format_key
from ..constants import (
    JSON_EXTENSIONS,
    YAML_EXTENSIONS,
    PYTHON_EXTENSIONS
)


class File(Adapter):
    def __init__(self, filepath, python_uppercase=True, *args, **kwargs):
        self.filepath = os.path.expanduser(filepath)
        self.python_uppercase = python_uppercase
        self.found = False

        # If strict parameter (inherited from parent) is True,
        # strictness_check routine will be called
        super(File, self).__init__(*args, **kwargs)

    def strictness_check(self):
        if not os.path.exists(self.filepath):
            raise IOError("Path {0} does not exist".format(self.filepath))

    def _okay(self, key):
        # Is all-uppercase required?
        if self.python_uppercase:
            return key.isupper()
        # If not, make sure we strip out any special variables
        return not key.startswith('__')

    def load(self, formatter=None):
        try:
            fd = open(self.filepath, 'r')
        except IOError:
            if self.strict is True:
                raise
            else:
                return

        _, file_extension = os.path.splitext(self.filepath)

        if file_extension.lower() in JSON_EXTENSIONS:
            import json
            self.data = dict((self.format(k, formatter), v) for k, v in json.load(fd).items())
        elif file_extension.lower() in YAML_EXTENSIONS:
            from yaml import load as yload, dump as ydump
            try:
                from yaml import CLoader as Loader
            except ImportError:
                from yaml import Loader
            self.data = dict((self.format(k, formatter), v) for k, v in yload(fd, Loader=Loader).items())
        elif file_extension.lower() in PYTHON_EXTENSIONS:
            mod = imp.load_source('mod', self.filepath)
            self.data = dict(
                (self.format(k, formatter), v)
                for k, v in vars(mod).items()
                if self._okay(k)
            )
        else:
            raise ValueError("Unhandled file extension {0}".format(file_extension))

        fd.close()
        self.found = True

    def __str__(self):
        return "File({0!r})".format(self.filepath)
