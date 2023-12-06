from functools import reduce
from typing import Any, Dict, List, Optional
from .baseoptions import BaseOptions
from .parameter import Parameter
from .exceptions import RequiredParameterMissingException, DuplicateOptionException
from .types import ParameterModel


class Options(BaseOptions[Dict[str, Any]]):
  def __init__(self,
               parameters: List[Parameter],
               argvs: List[str],
               env_prefix: Optional[str] = None,
               always_include_all: Optional[bool] = False
               ):
    """
    Parameters:
      - parameters: List of Parameter-objects that define the options
      - argvs: List of command line arguments
      - env_prefix: Prefix to apply to environment variable names
                    when looking for parameter values from the environment
      - always_include_all: Sets always_enable True for all Parameters
    """

    self._parameter_objects = parameters
    if always_include_all is True:
      for x in self._parameter_objects:
        x.always_include = True

    super().__init__(
        parameters=self._generate_parameter_models(
            self._parameter_objects),
        argvs=argvs,
        env_prefix=env_prefix
    )

    self._lookup_parameter_objects = {
        p.var_name: p for p in self._parameter_objects
    }

    """
    Example:
      parameters = [
        Parameter("host",   str,  "mqtt_host",  default="127.0.0.1"),
        Parameter("port",   int,  "mqtt_port"),
        Parameter("topic",  str,  "mqtt_topic"),
        Parameter("dir",    str,  "filename_dir"),
        Parameter("silent", Parameter.flag, "silent")
      ]
    """

  @staticmethod
  def _generate_parameter_models(parameter_objects: List[Parameter]) -> List[ParameterModel]:
    def var_names_reducer(result: Dict[str, List[str]], value: Parameter):
      if value.var_name not in result['unique']:
        result['unique'].append(value.var_name)
      else:
        result['duplicate'].append(value.var_name)
      return result

    var_names = reduce(
        var_names_reducer,
        parameter_objects,
        {'unique': [], 'duplicate': []}
    )

    if len(var_names['unique']) != len(parameter_objects):
      raise DuplicateOptionException(
          f'Duplicate variable names: {var_names["duplicate"]}')

    return [
        ParameterModel(
            default=p.default,
            description=p.description,
            examples=p.examples,
            is_flag=p.is_parameter_a_flag,
            is_optional=p.is_optional,
            long_name=p.name,
            short_name=p.short_name,
            title=p.name,
            types=p.types,
            name=p.var_name,
        ) for p in parameter_objects
    ]

  def eval(self) -> Dict[str, Any]:
    result = ({
        name: self._lookup_parameter_objects[name].func(value)
        for name, value in self._inputs.items()
    })

    # set defaults wherever they exist and no values have been inputted
    for parameter in self._parameter_objects:
      if (
          (parameter.default is not None or parameter.always_include is True) and
          parameter.var_name not in result
      ):
        result[parameter.var_name] = parameter.default

      if not parameter.is_optional and parameter.var_name not in result:
        raise RequiredParameterMissingException(
            f'Required parameter "{parameter.name}" missing',
            parameter=parameter.name
        )

    return result
