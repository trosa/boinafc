#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import __builtin__

# Install the new import function: 
def custom_import_install(path):
    _old__import__ = None # To keep the old __builtins__.__import__

    re_escaped_path_sep = re.escape(os.path.sep)  # os.path.sep escaped for re
    
    # Regular expression to match a directory of a web2py application relative to
    # the web2py install.
    # Like web2py installation dir path/applications/app_name/modules.
    # We also capture "applications/app_name" as a group.
    re_app_dir = re.compile(re_escaped_path_sep.join(
            (
                "^" + re.escape(path),
                "(" + "applications", 
                "[^", 
                "]+)", 
                "", 
                ) ))

    def _web2py__import__(name, globals={}, locals={}, fromlist=[], level=-1):
        """
        This new import function will try to import from applications.module.
        If this does not work, it falls back on the regular import method.
        @see: __builtins__.__import__
        """
        
        def _web2py__import__dot(prefix, name, globals, locals, fromlist, level):
            """
            Here we will import x.y.z as many imports like:
            from applications.app_name.modules import x
            from applications.app_name.modules.x import y
            from applications.app_name.modules.x.y import z.
            x will be the module returned.
            """
        
            result = None
            for name in name.split("."):
                new_mod = _old__import__(prefix, globals, locals, [name], level)
                try:
                    result = result or new_mod.__dict__[name]
                except KeyError:
                    raise ImportError()
                prefix += "." + name
            return result

        # if not relative and not from applications:
        if not name.startswith(".") and level <= 0 \
                and not name.startswith("applications."):
            # Get the name of the file do the import
            caller_file_name = globals.get("__file__", "")
            if not os.path.isabs(caller_file_name):
                # Make the path absolute
                caller_file_name = os.path.join(path, caller_file_name)
            # Is the path in an application directory?
            match_app_dir = re_app_dir.match(caller_file_name)
            if match_app_dir:
                try:
                    # Get the prefix to add for the import 
                    # (like applications.app_name.modules):
                    modules_prefix = \
                        ".".join((match_app_dir.group(1).replace(os.path.sep, "."), 
                                  "modules"))
                    if not fromlist:
                        # import like "import x" or "import x.y"
                        return _web2py__import__dot(modules_prefix, name, globals,
                                                    locals, fromlist, level)
                    else:
                        # import like "from x import a, b, ..."
                        return _old__import__(modules_prefix + "." + name, globals, 
                                              locals, fromlist, level)
                except ImportError:
                    pass
        return _old__import__(name, globals, locals, fromlist, level)   

    (_old__import__, __builtin__.__import__) = (__builtin__.__import__, _web2py__import__)

