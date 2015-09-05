import argparse
import logging
import re
import sys

from select import select

def _get_stdin():
  rlist, _, _ = select([sys.stdin], [], [], 0.1)
  if rlist:
    return (line.rstrip() for line in sys.stdin)
  else:
    return None

def _quote_args(arg):
  if re.search('\s', arg):
    return "'%s'" % arg
  return arg

def _values_to_str(values):
  return " ".join(map(_quote_args, values))

def build_merger(parser):
  def merger(args, leftovers):
    logging.debug("Merging %s and %s" % (args, leftovers))
    if not leftovers and not args.arguments:
      parser.error("Need to pass arguments or pipe via stdin")
    elif not leftovers:
      return
    elif args.source == 'arguments':
      (arguments,) = args.arguments
      leftovers_string = _values_to_str(leftovers)
      args.arguments = (" ".join([leftovers_string, arguments]),)
    elif args.source == None:
      leftovers_string = _values_to_str(leftovers)
      args.source = 'arguments'
      args.arguments = (leftovers_string,)
    else:
      parser.error("Can only take arguments via stdin or as input arguments")
  return merger

class ExtraArguments(argparse.Action):
  def __call__(self,parser,namespace,values,option_string=None):
    stdin_argument_list = _get_stdin()
    if stdin_argument_list and values:
      parser.error("Can only take arguments via stdin or as input arguments")
    elif stdin_argument_list:
      setattr(namespace, self.dest, stdin_argument_list)
      setattr(namespace, 'source', 'stdin')
    elif values:
      value_string = _values_to_str(values)
      setattr(namespace, self.dest, (value_string,))
      setattr(namespace, 'source', 'arguments')
    else:
      setattr(namespace, self.dest, [])
      setattr(namespace, 'source', None)

def get_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--database', type=argparse.FileType('w'),
                      default=open('.argumentsQueue', 'ab'))
  subparsers = parser.add_subparsers(help='sub-command help')

  put_parser = subparsers.add_parser('put')
  put_parser.add_argument('arguments', type=str, action=ExtraArguments,
                          nargs=argparse.REMAINDER,
                          metavar="...",
                          help="Arguments here or via stdin but not both")
  put_parser.set_defaults(sub_command='put', merge_leftovers=build_merger(put_parser))

  pop_parser = subparsers.add_parser('pop')
  pop_parser.set_defaults(sub_command='pop')

  args, leftovers = parser.parse_known_args()
  try:
    args.merge_leftovers(args, leftovers)
  except AttributeError:
    pass
  
  return args
