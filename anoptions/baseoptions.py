import getopt
from typing import Dict, List, Optional, Generic, TypeVar
from .env import Env
from .exceptions import DuplicateOptionException
from .types import LookupVariables, ParameterModel

T = TypeVar("T")


class BaseOptions(Generic[T]):
  def __init__(self,
               parameters: List[ParameterModel],
               argvs: List[str],
               env_prefix: Optional[str] = None,
               ):

    super().__init__()

    self._parameters = parameters
    self._argvs = argvs
    self._env_prefix = env_prefix.upper() if isinstance(env_prefix, str) else None

    self._env_var_map = self._create_env_var_map(
        parameters=self._parameters,
        env_prefix=self._env_prefix
    )

    self._check_duplicates(
        parameters=self._parameters
    )

    self._lookup = self._generate_lookup_variables(
        parameters=self._parameters
    )

    self._inputs = self._get_inputs()

  @staticmethod
  def _create_env_var_map(
      parameters: List[ParameterModel],
      env_prefix: Optional[str] = None
  ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    if env_prefix is not None:
      for parameter in parameters:
        result[f'{env_prefix}_{parameter.long_name.upper()}'] = parameter.name
    return result

  @staticmethod
  def _check_duplicates(parameters: List[ParameterModel]) -> None:
    _short: List[str] = []
    _long: List[str] = []

    for parameter in parameters:
      if parameter.long_name in _long:
        raise DuplicateOptionException(f'--{parameter.long_name}')
      if parameter.short_name in _short:
        raise DuplicateOptionException(f'-{parameter.short_name}')

      _long.append(parameter.long_name)
      _short.append(parameter.short_name)

  @classmethod
  def _generate_lookup_variables(cls, parameters: List[ParameterModel]) -> LookupVariables:
    cls._check_duplicates(parameters)
    result_short = [
        parameter.short_name + ('' if parameter.is_flag else ':') for parameter in parameters
    ]
    result_long = [
        parameter.long_name + ('' if parameter.is_flag else '=') for parameter in parameters
    ]
    result_lookup_opt = {}
    result_lookup_name = {}
    for parameter in parameters:
      result_lookup_opt[f'--{parameter.long_name}'] = parameter
      result_lookup_opt[f'-{parameter.short_name}'] = parameter
      result_lookup_name[parameter.name] = parameter

    return LookupVariables(
        shortopts=''.join(result_short),
        longopts=result_long,
        lookup_option=result_lookup_opt,
        lookup_name=result_lookup_name
    )

  def _get_inputs(self) -> Dict[str, str]:
    # Get inputs from environment variables
    env_inputs = Env.get_kv_from_env(self._env_var_map)

    # Get inputs from command line parameters; will raise getopt.GetoptError if fails
    argv_opts, _ = getopt.getopt(
        self._argvs,
        self._lookup.shortopts,
        self._lookup.longopts
    )

    argv_inputs = {
        self._lookup.lookup_option[option].name: value
        for option, value in argv_opts if option in self._lookup.lookup_option.keys()
    }

    inputs = {
        **env_inputs,
        **argv_inputs
    }

    flags = [x.name for x in self._parameters if x.is_flag]

    for name, value in inputs.items():
      if name in flags and (value is None or len(value) == 0):
        inputs[name] = 'true'

    return inputs

  def usage(self, appname: str) -> str:
    doc: List[str] = [
        f'USAGE: {appname} [OPTION ...] ...',
        ''
        'Options:',
        ''
    ]

    for parameter_model in self._parameters:
      types_list = [
          typ for typ in parameter_model.types if typ is not None]
      types = f'[{" | ".join(types_list)}]{" (optional)" if parameter_model.is_optional else ""}'

      default = (
          f' (default: {parameter_model.default})'
          if parameter_model.default and parameter_model.is_flag is False
          else ''
      )

      description = (
          parameter_model.description if parameter_model.description else parameter_model.title)

      doc += [
          f'-{parameter_model.short_name} --{parameter_model.long_name} {types}{default}',
          f'\t{description}',
      ]

      if parameter_model.examples:
        doc.append(
            f'\tExamples: {", ".join(parameter_model.examples)}')
      doc.append('')

    return '\n'.join(doc)

  def eval(self) -> T:
    raise NotImplementedError('Child class should implement eval()')
