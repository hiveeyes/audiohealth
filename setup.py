# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

requires = [
    'docopt==0.6.2',
    'ansicolors==1.1.8',
    'matplotlib',
    'scipy',
    'numpy',
]

extras = {
}

setup(name='audiohealth',
      version='0.4.0',
      description='',
      long_description='',
      license="AGPL 3",
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS"
        ],
      author='The Hiveeyes Developers',
      author_email='hello@hiveeyes.org',
      url='https://github.com/hiveeyes/audiohealth',
      packages=find_packages(),
      include_package_data=True,
      package_data={
      },
      zip_safe=False,
      install_requires=requires,
      extras_require=extras,
      dependency_links=[
      ],
      entry_points={
          'console_scripts': [
              'audiohealth         = audiohealth:main',
          ],
      },
)
