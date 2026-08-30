import os, site

# Dynamically include site-packages mcp directory in package __path__
for sp in site.getsitepackages():
    pkg_dir = os.path.join(sp, "mcp")
    if os.path.isdir(pkg_dir) and pkg_dir not in __path__:
        __path__.append(pkg_dir)

