from setuptools import setup

__version__ = '0.1.0'

setup(
  name='jobqueue',
  version=__version__,
  licence='MIT',
  install_requires=[],
  test_suite='jobqueue.tests',
  tests_require=[],
  packages=['jobqueue'],
  scripts=['scripts/jobqueue']
)
