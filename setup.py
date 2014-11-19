#!/usr/bin/env python

from setuptools import setup, find_packages

requires = []

setup(name='cckit',
      version='0.1',
      classifiers=[
          "Programming Language :: Python",
      ],
      packages=find_packages(),
      zip_safe=False,
      install_requires=requires,
      test_suite="tests"
      )
