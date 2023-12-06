import os
from typing import Optional
from unittest import TestCase, mock, main
from pydantic import Field, ValidationError
from anoptions import TypedOptions, BaseOptionsModel
from anoptions.exceptions import DuplicateOptionException


class DefaultTestModel(BaseOptionsModel):
  mqtt_host: str = Field(
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
  timeout: Optional[int] = Field(
      default=10,
      json_schema_extra={
          "short_name": 'T'
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


class DuplicateShortNameModel(BaseOptionsModel):
  directory: Optional[str] = None
  delta: Optional[str] = None


class DuplicateLongNameModel(BaseOptionsModel):
  directory: Optional[str] = None
  dir: Optional[str] = Field(
      default=None,
      json_schema_extra={
          "long_name": 'directory'
      }
  )


@mock.patch.dict(os.environ, {"APPNAME_TOPIC": "foobar"})
class TestTypedOptions(TestCase):
  def test_options(self):
    """
    Test that we can evaluate options
    """
    argvs = ['--host', 'localhost', '-p', '2000']
    options = TypedOptions(model=DefaultTestModel,
                           argvs=argvs, env_prefix='APPNAME').eval()
    self.assertEqual(
        options.model_dump(),
        {
            'mqtt_port': 2000,  # tests short name
            'mqtt_topic': 'foobar',  # tests env input
            'mqtt_host': 'localhost',  # tests long name
            'directory': None,  # tests always_include
            'silent': False,  # "flags" are False is not present
            'timeout': 10,  # tests default value
            'delta': None  # with TypedOptions, all attributes are always included
        }
    )

  def test_throw_on_duplicate_short_name(self):
    """
    Test that we raise an exception if there are duplicate short names
    """
    self.assertRaises(
        DuplicateOptionException,
        TypedOptions,
        model=DuplicateShortNameModel,
        argvs=[]
    )

  def test_throw_on_duplicate_long_name(self):
    """
    Test that we raise an exception if there are duplicate long names
    """
    self.assertRaises(
        DuplicateOptionException,
        TypedOptions,
        model=DuplicateLongNameModel,
        argvs=[]
    )

  def test_throw_on_missing_required_parameter(self):
    """
    Test that we raise an exception if there are missing required parameters
    """
    options = TypedOptions(model=DefaultTestModel, argvs=[])
    self.assertRaises(
        ValidationError,
        options.eval,
    )


if __name__ == '__main__':
  main()
