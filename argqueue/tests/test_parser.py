import logging
import unittest

from mock import patch
from StringIO import StringIO
from unittest import skip

from argqueue.parser import get_arguments

class TestParser(unittest.TestCase):
  @patch('sys.stderr')
  @patch('sys.argv')
  def test_unknown_subcommand(self, argv_mock, stderr_mock):
    argv = ['SCRIPT_NAME', 'foo', 'bar baz']
    argv_mock.__getitem__.side_effect = argv.__getitem__
    self.assertRaises(SystemExit, get_arguments)

  @patch('sys.argv')
  def test_put_good_arguments(self, argv_mock):
    argv = ['SCRIPT_NAME', 'put', 'bar baz', 'quux']
    argv_mock.__getitem__.side_effect = argv.__getitem__
    args = get_arguments()
    self.assertEqual(args.sub_command, 'put')
    self.assertEqual(list(args.arguments), ["'bar baz' quux"])

  @patch('argqueue.parser._get_stdin')
  @patch('sys.argv')
  def test_put_good_stdin(self, argv_mock, stdin_mock):
    argv = ['SCRIPT_NAME', 'put']
    argv_mock.__getitem__.side_effect = argv.__getitem__
    stdin_mock.return_value = ["'bar baz' quux"]
    args = get_arguments()
    self.assertEqual(args.sub_command, 'put')
    self.assertEqual(list(args.arguments), ["'bar baz' quux"])

  @patch('sys.stderr')
  @patch('argqueue.parser._get_stdin')
  @patch('sys.argv')
  def test_put_stdin_and_argv(self, argv_mock, stdin_mock, stderr_mock):
    argv = ['SCRIPT_NAME', 'put', 'foo']
    argv_mock.__getitem__.side_effect = argv.__getitem__
    stdin_mock.return_value = ["'bar baz' quux"]
    self.assertRaises(SystemExit, get_arguments)

  @patch('sys.argv')
  def test_put_good_arguments_with_options(self, argv_mock):
    argv = ['SCRIPT_NAME', 'put', '--foo', 'bar baz', 'quux']
    argv_mock.__getitem__.side_effect = argv.__getitem__
    args = get_arguments()
    self.assertEqual(args.sub_command, 'put')
    self.assertEqual(list(args.arguments), ["--foo 'bar baz' quux"])

  @skip("Gets confused by help arguments")
  @patch('sys.argv')
  def test_put_help_argument(self, argv_mock):
    argv = ['SCRIPT_NAME', 'put', '-h', '--foo', 'bar baz', 'quux']
    argv_mock.__getitem__.side_effect = argv.__getitem__
    args = get_arguments()
    self.assertEqual(args.sub_command, 'put')
    self.assertEqual(list(args.arguments), ["-h --foo 'bar baz' quux"])

  @patch('argqueue.parser._get_stdin')
  @patch('sys.argv')
  def test_put_help_stdin(self, argv_mock, stdin_mock):
    argv = ['SCRIPT_NAME', 'put']
    argv_mock.__getitem__.side_effect = argv.__getitem__
    stdin_mock.return_value = ["-h 'bar baz' quux"]
    args = get_arguments()
    self.assertEqual(args.sub_command, 'put')
    self.assertEqual(list(args.arguments), ["-h 'bar baz' quux"])

if __name__ == '__main__':
  logging.basicConfig(level=logging.WARN)
  unittest.main()
