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

def _quote_job(job):
  if re.search('\s', job):
    return "'%s'" % job
  return job

def _values_to_str(values):
  return " ".join(map(_quote_job, values))

def build_merger(parser):
  def merger(args, leftovers):
    logging.debug("Merging %s and %s" % (args, leftovers))
    if not leftovers and not args.jobs:
      parser.error("Need to pass arguments or pipe via stdin")
    elif not leftovers:
      return
    elif args.source == 'arguments':
      (jobs,) = args.jobs
      leftovers_string = _values_to_str(leftovers)
      args.jobs = (" ".join([leftovers_string, jobs]),)
    elif args.source == None:
      leftovers_string = _values_to_str(leftovers)
      args.source = 'arguments'
      args.jobs = (leftovers_string,)
    else:
      parser.error("Can only take jobs via stdin or as input arguments")
  return merger

class ExtraArguments(argparse.Action):
  def __call__(self,parser,namespace,values,option_string=None):
    stdin_jobs_list = _get_stdin()
    if stdin_jobs_list and values:
      parser.error("Can only take jobs via stdin or as input arguments")
    elif stdin_jobs_list:
      setattr(namespace, 'jobs', stdin_jobs_list)
      setattr(namespace, 'source', 'stdin')
    elif values:
      value_string = _values_to_str(values)
      setattr(namespace, 'jobs', (value_string,))
      setattr(namespace, 'source', 'arguments')
    else:
      setattr(namespace, 'jobs', [])
      setattr(namespace, 'source', None)

def build_parser():
  parser = argparse.ArgumentParser(description="Persistent queue of jobs")
  parser.add_argument('-d', '--database', type=argparse.FileType('ab'),
                      default=open('.jobsQueue', 'ab'),
                      help="Path to the queue database (default: .jobsQueue)")
  subparsers = parser.add_subparsers(help='sub-commands')

  done_parser = subparsers.add_parser('done',
                                      help="Mark job as 'done'",
                                      description="Used to mark job as 'done'")
  done_parser.add_argument('job_id', type=int, metavar='id',
                           help="id as given by lease or used by get")
  done_parser.set_defaults(sub_command='done')

  exit_parser = subparsers.add_parser('exit',
                                      help="Mark job as 'exit'",
                                      description="Used to mark job as 'exit'")
  exit_parser.add_argument('job_id', type=int, metavar='id',
                           help="id as given by lease or used by get")
  exit_parser.set_defaults(sub_command='exit')

  get_parser = subparsers.add_parser('get',
                                     help="Get job for the given id",
                                     description="Used to get job specified by 'id'")
  get_parser.add_argument('job_id', type=int, metavar='id',
                          help="id as given by lease")
  get_parser.set_defaults(sub_command='get')

  lease_parser = subparsers.add_parser('lease',
                                      help="Lease a job to use with 'get'",
                                      description="Lease a job and get its 'id'")

  lease_parser.add_argument('-t', '--timeout', type=int,
                            help="Lease timeout in seconds (default: 1 hour)",
                            default=3600)
  lease_parser.add_argument('job_id', type=int,
                            help="Optional: re-lease a job",
                            nargs="?")
  lease_parser.set_defaults(sub_command='lease')

  pop_parser = subparsers.add_parser('pop',
                                     help="Pop next available job",
                                     description="Get the next job.  It's better to lease one if possible though")
  pop_parser.set_defaults(sub_command='pop')

  put_parser = subparsers.add_parser('put',
                                     help="Add job to the queue",
                                     description="Add job to the queue")
  put_parser.add_argument('arguments', type=str, action=ExtraArguments,
                          nargs=argparse.REMAINDER,
                          metavar="...",
                          help="Job details here or via stdin but not both")
  put_parser.set_defaults(sub_command='put', merge_leftovers=build_merger(put_parser))

  status_parser = subparsers.add_parser('status',
                                        help="List the status of jobs",
                                        description="List the status of jobs")
  status_parser.add_argument('job_ids', nargs='*',
                             help="List of jobs you want the status of (default: all jobs)")
  status_parser.set_defaults(sub_command='status')

  return parser

def get_arguments():
  parser = build_parser()
  args, leftovers = parser.parse_known_args()
  try:
    args.merge_leftovers(args, leftovers)
  except AttributeError:
    pass
  return args
