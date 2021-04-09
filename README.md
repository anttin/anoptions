# anoptions

A python3 module to assist in defining application options and collecting user input for them from command line and environment variables.

## Install

`pip3 install anoptions`

## Usage

Follow the example. If short_name is omitted, the first letter of the "long" name parameter is used. Duplicate short or long names are not allowed.

Func is a required parameter. Give a function that converts the inputted value to the proper data type. If no conversion is desired, you can use `Parameter.dummy`.
For flags where existence of a variable will always mark True use `Parameter.flag`.
For flags where a more logical input parsing (for example silent='false' to be interpreted as False) is desired use `Parameter.bool` (or just `bool`).


## Example

Code (main.py):

```python
from anoptions import Parameter, Options

def main(argv):
  parameters = [
    Parameter("host",   str,  "mqtt_host"),
    Parameter("port",   int,  "mqtt_port"),
    Parameter("topic",  str,  "mqtt_topic"),
    Parameter("dir",    str,  "directory"),
    Parameter("delta",  int,  "delta", short_name='D'),
    Parameter("silent", bool, "silent")
  ]

  opt = Options(parameters, argv, 'appname')

  d = opt.eval()
  print(d)


if __name__ == "__main__":
  main(sys.argv[1:])
```

Run:

```shell
APPNAME_PORT=1232 APPNAME_SILENT=1 python3 main.py -d /tmp --host 10.1.2.3 -D 60
{'mqtt_port': 1232, 'silent': True, 'filename_dir': '/tmp', 'mqtt_host': '10.1.2.3', 'delta': 60}
```

