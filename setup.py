#! /usr/bin/env python3

import os

try:
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup

NAME = 'OASYS1-WOFRY'
VERSION = '1.0.26'
ISRELEASED = False

DESCRIPTION = 'WOFRY (Wave Optics FRamework in pYthon)'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.md')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Manuel Sanchez del Rio, Luca Rebuffi'
AUTHOR_EMAIL = 'lrebuffi@anl.gov'
URL = 'https://github.com/oasys-kit/OASYS-WOFRY'
DOWNLOAD_URL = 'https://github.com/oasys-kit/OASYS-WOFRY'
LICENSE = 'GPLv3'

KEYWORDS = (
    'simulator',
    'waveoptics',
    'oasys1',
)

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Science/Research',
)

SETUP_REQUIRES = (
    'setuptools',
)

INSTALL_REQUIRES = (
    'oasys1>=1.2.45',
    'wofryimpl>=1.0.7'
)

PACKAGES = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests'))

PACKAGE_DATA = {
    "orangecontrib.wofry.widgets.wavefront_propagation":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.wofry.widgets.beamline_elements":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.wofry.widgets.tools":["icons/*.png", "icons/*.jpg"],
}

NAMESPACE_PACAKGES = ["orangecontrib", "orangecontrib.wofry", "orangecontrib.wofry.widgets"]

ENTRY_POINTS = {
    'oasys.addons' : ("wofry = orangecontrib.wofry", ),
    'oasys.widgets' : (
        "Wofry Wavefront Propagation = orangecontrib.wofry.widgets.wavefront_propagation",
        "Wofry Optical Elements = orangecontrib.wofry.widgets.beamline_elements",
        "Wofry Tools = orangecontrib.wofry.widgets.tools",
    ),
}

if __name__ == '__main__':
    try:
        import PyMca5, PyQt4

        raise NotImplementedError("This package doesn't work with Oasys1 beta.\nPlease install OASYS1 final release: http://www.elettra.eu/oasys.html")
    except:
        setup(
              name = NAME,
              version = VERSION,
              description = DESCRIPTION,
              long_description = LONG_DESCRIPTION,
              author = AUTHOR,
              author_email = AUTHOR_EMAIL,
              url = URL,
              download_url = DOWNLOAD_URL,
              license = LICENSE,
              keywords = KEYWORDS,
              classifiers = CLASSIFIERS,
              packages = PACKAGES,
              package_data = PACKAGE_DATA,
              setup_requires = SETUP_REQUIRES,
              install_requires = INSTALL_REQUIRES,
              entry_points = ENTRY_POINTS,
              namespace_packages=NAMESPACE_PACAKGES,
              include_package_data = True,
              zip_safe = False,
              )
