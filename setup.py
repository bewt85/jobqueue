from setuptools import setup

__version__ = '0.1.0'

setup(
  name='argqueue',
  version=__version__,
  licence='MIT',
  install_requires=[],
  test_suite='argqueue.tests',
  tests_require=[],
  packages=['argqueue'],
  scripts=['scripts/argqueue']
)
