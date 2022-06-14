#!/usr/bin/env python3
import glob
import os
import sys
from typing import List

from setuptools import setup, find_packages

requirements_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'requirements.txt'))
if not os.path.isfile(requirements_file):
    raise RuntimeError("Could not find a requirements.txt")

install_requires = []
with open(requirements_file) as f:
    for req in f.read().splitlines():
        req = req.strip()
        if req != '' and not req.startswith('#'):
            install_requires.append(req)

# Include fastiot. Please note that we have to prevent __init__.py file inside fastiot from being executed because it
# would trigger package imports which may fail.
_python_src_dir = os.path.join(os.path.dirname(__file__), 'src', 'fastiot', 'cli')
if _python_src_dir not in sys.path:
    sys.path.append(_python_src_dir)

# See upper comment. Most likely your IDE will mark these imports as missing which you can ignore.
from constants import template_dir
from version import create_version_file, get_version


create_version_file(destination='src/fastiot/__version__.py')


def get_package_data_for_templates() -> List[str]:
    fastiot_dir = os.path.join(template_dir, '**')
    files = list(glob.glob(fastiot_dir, recursive=True))
    files = [f for f in files if os.path.isfile(f)]
    return files


package_data = get_package_data_for_templates()
package_data.append(requirements_file)

setup(
    name='fastiot',
    version=get_version(complete=True),
    description='Fast IoT',
    author='Fraunhofer IVV',
    author_email='tilman.klaeger@ivv-dd.fraunhofer.de;konstantin.merker@ivv-dd.fraunhofer.de',
    url='https://redmine.ivv-dd.fhg.de/projects/fastiot',
    packages=find_packages("src", include=["fastiot", "fastiot.*"]),
    package_dir={"": "src"},
    package_data={"fastiot": package_data},
    scripts=['src/fastiot/version.py', 'src/fastiot/nuitka_compile.py'],
    python_requires='~=3.8',
    install_requires=install_requires
)