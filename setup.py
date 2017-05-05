#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path

import version

__version__ = version.version


# get the dependencies and installs:
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]


setup(name='subsync',
      version=__version__,
      author='Slava Kerner',
      author_email='slava.kerner@gmail.com',
      packages=find_packages(exclude=["tests"]),
      include_package_data=True,
      description="Subtitles synchronisation",
      install_requires=install_requires,
      dependency_links=dependency_links,
      entry_points={'console_scripts': ['subsync = subsync.cli:cli']},
      license="GPLv3",
      platforms=["Independent"],
      keywords="subsync subtitle sync",
      url="https://github.com/slava-kerner/subsync",
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Multimedia :: Video",
          "Topic :: Multimedia :: Sound/Audio :: Speech",
          "Topic :: Software Development :: Libraries",
          "Topic :: Text Processing :: Markup",
      ]
      )
