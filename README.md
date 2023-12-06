# anoptions

A python3 module to assist in defining application options and collecting user input for them from command line and environment variables.

## Install

`pip3 install anoptions`

## Classic mode

Classic mode provides the same functionality that has existed from the initial release. Evaluating the
arguments results in an untyped dictionary.

### Usage (classic)

Follow the example. If short_name is omitted, the first letter of the "long" name parameter is used. Duplicate short or long names are not allowed.

Func is a required parameter. Give a function that converts the inputted value to the proper data type. If no conversion is desired, you can use `Parameter.dummy`.
For flags where existence of a variable will always mark True use `Parameter.flag`.
For flags where a more logical input parsing (for example silent='false' to be interpreted as False) is desired use `Parameter.bool` (or just `bool`).

### Example (classic)

Code (main.py):

```python
import sys
from anoptions import Parameter, Options

def main(argvs):
  parameters = [
    Parameter("host",   str,            "mqtt_host",  default='127.0.0.1',
                                                      description='MQTT Host address',
                                                      examples=['127.0.0.1', 'localhost']),
    Parameter("port",   int,            "mqtt_port",  default=1883),
    Parameter("topic",  str,            "mqtt_topic", required=True),
    Parameter("dir",    str,            "directory",  always_include=True),
    Parameter("delta",  int,            "delta",      short_name='D'),
    Parameter("silent", Parameter.flag, "silent")
  ]

  app_name = 'APPNAME'
  o = Options(parameters=parameters, argvs=argvs, env_prefix=app_name)
  options = o.eval()

  # Print all values
  print('all values', options)

  # Print a specific value
  print('host', options['mqtt_host'])

  # Print usage output
  print(o.usage(app_name))


if __name__ == "__main__":
  main(sys.argv[1:])
```

Run:

```shell
$ APPNAME_PORT=1232 APPNAME_SILENT=1 python3 main.py -d /tmp --host 10.1.2.3 -D 60 -t foobar

all values {'mqtt_port': 1232, 'silent': True, 'directory': '/tmp', 'mqtt_host': '10.1.2.3', 'delta': 60, 'mqtt_topic': 'foobar'}
host 10.1.2.3
USAGE: APPNAME [OPTION ...] ...
Options:

-h --host [str] (optional) (default: 127.0.01)
        MQTT Host address
        Examples: 127.0.0.1, localhost

-p --port [int] (optional) (default: 1883)
        port

-t --topic [str]
        topic

-d --dir [str] (optional)
        dir

-D --delta [int] (optional)
        delta

-s --silent [flag] (optional)
        silent
```

## Typed mode

Typed mode exists since version 2.0. It provides similar functionality to the classic mode,
but with a completely different way of operation. In typed mode, instead of defining `Parameters`,
you define one pydantic model and use that model to prepare the inputs. Evaluating the arguments
results a typed class.

### Usage (typed)

Follow the example. If short_name is omitted, the first letter of the "long" name parameter is used. Duplicate short or long names are not allowed. Defining a "variable name" like in classic mode is not supported as it does not make any sense.

Instead of providing functions for type conversion from inputs, this mode of operation uses pydantic's
automatic type conversion.

### Example (typed)

Code (main.py):

```python
import sys
from anoptions import TypedOptions, BaseOptionsModel
from pydantic import Field
from typing import Optional


class OptionsModel(BaseOptionsModel):
    mqtt_host: str = Field(
        default='127.0.0.1',
        description='MQTT host address',
        examples=['127.0.0.1', 'localhost'],
        json_schema_extra={
            "long_name": 'host',
            "short_name": 'h'
        }
    )
    mqtt_port: int = Field(
        default=1883,
        json_schema_extra={
           "long_name": 'port',
            "short_name": 'p'
        }
    )
    mqtt_topic: str = Field(
        json_schema_extra={
            "long_name": 'topic',
            "short_name": 't'
        }
    )
    directory: Optional[str] = None
    delta: Optional[int] = Field(
        default=None,
        json_schema_extra={
            "short_name": 'D'
        }
    )    
    silent: Optional[bool] = False


def main(argv):
  app_name = 'appname'
  o = TypedOptions(model=OptionsModel, argvs=argvs, env_prefix=app_name)
  options = o.eval()

  # Print all values
  print('all values', options)

  # Print a specific value
  print('host', options.mqtt_host)

  # Get a dict output  
  print('dict', options.model_dump())

  # Print usage output
  print(o.usage(app_name))


if __name__ == "__main__":
  main(sys.argv[1:])
```

Run:

```shell
$ APPNAME_PORT=1232 APPNAME_SILENT=1 python3 main.py -d /tmp --host 10.1.2.3 -D 60 -t foobar

all values mqtt_host='10.1.2.3' mqtt_port=1232 mqtt_topic='foobar' directory='/tmp' delta=60 silent=True
host 10.1.2.3
dict {'mqtt_host': '10.1.2.3', 'mqtt_port': 1232, 'mqtt_topic': 'foobar', 'directory': '/tmp', 'delta': 60, 'silent': True}
USAGE: appname [OPTION ...] ...
Options:

-h --host [string] (default: 127.0.0.1)
        MQTT host address
        Examples: 127.0.0.1, localhost

-p --port [integer] (default: 1883)
        Mqtt Port

-t --topic [string]
        Mqtt Topic

-d --directory [string] (optional)
        Directory

-D --delta [integer] (optional)
        Delta

-s --silent [boolean] (optional)
        Silent

```

## Development

Run unit tests:

```shell
python3 -m unittest -v tests
```

Linting:

```shell
pylint anoptions
```
