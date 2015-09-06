# Argqueue

Queue up arguments to be run later.

Argqueue can be used to simpy 'put' and 'pop' arguments.  You can also
'lease' arguments for a given timeout.  If the task ends successfully
you can mark it as 'done'; if it fails, you can mark it as 'exit'

Argqueue is useful to keep track of which arguments you've invoked a
command with and whether they were OK, failed or timed out.

## Usage

```
# Load up some arguments
argqueue put foo
echo 'bar "baz quux"' | argqueue put

# Simple pop
echo $(argqueue pop)

# Lease example
arg_id=$(argqueue lease -t 20) # lease some arguments for 20s
echo $(argqueue get $arg_id)
if [ $? -eq 0 ]; then
  argqueue done $arg_id
else
  argqueue exit $arg_id
fi

# Database layout
$ echo "SELECT * FROM Arguments;" | sqlite3 .argumentsQueue -cmd ".header on"
Id|Args|Created|Status|Timeout
1|foo|1441578109|UNKNOWN|0
2|bar "baz quux"|1441578115|DONE|1441578156
```

## Install

```
pip install git+https://github.com/bewt85/argqueue.git
```

## Known Issues

If you need to include `-h` or `--help` in your arguments, you need to pass
them via stdin.
