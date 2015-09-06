# Jobqueue

Queue up jobs to be run later.

Jobqueue can be used to simpy 'put' and 'pop' jobs to run later.
You can also 'lease' a job for a given timeout.  If the task ends 
successfully you can mark it as 'done'; if it fails, you can mark it
as 'exit'.

Jobqueue is useful to keep track of which jobs you've run and
whether they were OK, failed or timed out.

## Usage

```
# Load up some arguments
jobqueue put echo foo
echo 'echo bar "baz quux"' | jobqueue put

# Simple pop
$(jobqueue pop)

# Lease example
arg_id=$(jobqueue lease -t 20) # lease some arguments for 20s
$(jobqueue get $arg_id)
status=$?
if [[ $status -eq 0 ]]; then
  jobqueue done $arg_id
else
  jobqueue exit $arg_id
fi
```

# Database layout
```
$ echo "SELECT * FROM Jobs;" | sqlite3 .jobsQueue -cmd ".header on"
Id|Details|Created|Status|Timeout
1|echo foo|1441582092|UNKNOWN|0
2|echo bar "baz quux"|1441582098|DONE|1441582133
```

## Install

```
pip install git+https://github.com/bewt85/jobqueue.git
```

## Known Issues

If you need to include `-h` or `--help` in your job, you need to pass it
via stdin.
