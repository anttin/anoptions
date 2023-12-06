import os
from anoptions import Parameter, Options
from anoptions.exceptions import DuplicateOptionException, RequiredParameterMissingException
from typing import List
from unittest import TestCase, mock, main

@mock.patch.dict(os.environ, {"APPNAME_TOPIC": "foobar"})
class TestOptions(TestCase):
    @staticmethod
    def get_default_parameters() -> List[Parameter]:
        return [
            Parameter("host",    str,            "mqtt_host",  default='127.0.0.1'),
            Parameter("port",    int,            "mqtt_port",  default=1883),
            Parameter("topic",   str,            "mqtt_topic", required=True),
            Parameter("timeout", int,            "timeout",    default=10, short_name='T'),
            Parameter("dir",     str,            "directory",  always_include=True),
            Parameter("delta",   int,            "delta",      short_name='D'),
            Parameter("silent",  Parameter.flag, "silent")
        ]

    def test_options_and_parameters(self):
        """
        Test that we can evaluate options with parameters
        """
        argvs = ['--host', 'localhost', '-p', '2000']
        parameters = self.get_default_parameters()
        options = Options(parameters=parameters, argvs=argvs, env_prefix='APPNAME').eval()
        self.assertEqual(
            options,
            {
                'mqtt_port': 2000, # tests short name
                'mqtt_topic': 'foobar', # tests env input
                'mqtt_host': 'localhost', # tests long name
                'directory': None, # tests always_include
                'silent': False, # tests flag default to False is not present
                'timeout': 10 # tests default value
                # missing 'delta' tests missing value without always_include 
            }
        )

    def test_throw_on_duplicate_short_name(self):
        """
        Test that we raise an exception if there are duplicate short names
        """
        parameters = [
            Parameter("dir",   str, "directory"),
            Parameter("delta", int, "delta"),
        ] 
        self.assertRaises(
            DuplicateOptionException,
            Options,
            parameters=parameters,
            argvs=[]
        )

    def test_throw_on_duplicate_long_name(self):
        """
        Test that we raise an exception if there are duplicate long names
        """
        parameters = [
            Parameter("directory", str, "directory"),
            Parameter("directory", int, "dir"),
        ] 
        self.assertRaises(
            DuplicateOptionException,
            Options,
            parameters=parameters,
            argvs=[]
        )


    def test_throw_on_duplicate_var_name(self):
        """
        Test that we raise an exception if there are duplicate variable names
        """
        parameters = [
            Parameter("foo", str, "directory"),
            Parameter("bar", str, "directory"),
        ] 
        self.assertRaises(
            DuplicateOptionException,
            Options,
            parameters=parameters,
            argvs=[]
        )

    def test_throw_on_missing_required_parameter(self):
        """
        Test that we raise an exception if there are missing required parameters
        """
        parameters = [Parameter("directory", str, "directory", required=True)]
        options = Options(parameters=parameters, argvs=[])
        self.assertRaises(
            RequiredParameterMissingException,
            options.eval
        )


if __name__ == '__main__':
    main()