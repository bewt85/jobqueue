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

def build_parser():
  parser = argparse.ArgumentParser(description="Persistent queue of arguments")
  parser.add_argument('-d', '--database', type=argparse.FileType('ab'),
                      default=open('.argumentsQueue', 'ab'),
                      help="Path the queue database (default: .argumentsQueue)")
  subparsers = parser.add_subparsers(help='sub-commands')

  done_parser = subparsers.add_parser('done',
                                      help="Mark arguments as 'done'",
                                      description="Used to mark arguments as 'done'")
  done_parser.add_argument('args_id', type=int, metavar='id',
                           help="id as given by lease or used by get")
  done_parser.set_defaults(sub_command='done')

  exit_parser = subparsers.add_parser('exit',
                                      help="Mark arguments as 'exit'",
                                      description="Used to mark arguments as 'exit'")
  exit_parser.add_argument('args_id', type=int, metavar='id',
                           help="id as given by lease or used by get")
  exit_parser.set_defaults(sub_command='exit')

  get_parser = subparsers.add_parser('get',
                                     help="Get arguments for given id",
                                     description="Used to get arguments specified by 'id'")
  get_parser.add_argument('args_id', type=int, metavar='id',
                          help="id as given by lease")
  get_parser.set_defaults(sub_command='get')

  lease_parser = subparsers.add_parser('lease',
                                      help="Lease some arguments to use with 'get'",
                                      description="Lease some arguments and get their 'id' of some arguments")

  lease_parser.add_argument('-t', '--timeout', type=int,
                            help="Lease timeout in seconds (default: 1 hour)",
                            default=3600)
  lease_parser.set_defaults(sub_command='lease')

  pop_parser = subparsers.add_parser('pop',
                                     help="Pop next available arguments",
                                     description="Get the next arguments.  It's better to lease them if possible though")
  pop_parser.set_defaults(sub_command='pop')

  put_parser = subparsers.add_parser('put',
                                     help="Add arguments to the queue",
                                     description="Add arguments to the queue")
  put_parser.add_argument('arguments', type=str, action=ExtraArguments,
                          nargs=argparse.REMAINDER,
                          metavar="...",
                          help="Arguments here or via stdin but not both")
  put_parser.set_defaults(sub_command='put', merge_leftovers=build_merger(put_parser))

  return parser

def get_arguments():
  parser = build_parser()
  args, leftovers = parser.parse_known_args()
  try:
    args.merge_leftovers(args, leftovers)
  except AttributeError:
    pass
  return args
