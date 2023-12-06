import re
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Union
from .exceptions import InvalidModelClassException
from .types import BaseOptionsModel, ParameterModel, ModelJsonSchema
from .baseoptions import BaseOptions

T = TypeVar('T', bound=BaseOptionsModel)


class TypedOptions(BaseOptions[T], Generic[T]):
  def __init__(self,
               model: Type[T],
               argvs: List[str],
               env_prefix: Optional[str] = None,
               ):
    """
    Parameters:
      - model: Pydantic model class defining the input parameters;
               must inherit anoptions.types.BaseOptionsModel
      - argvs: List of command line arguments
      - env_prefix: Prefix to apply to environment variable names
                    when looking for parameter values from the environment
    """

    if not issubclass(model, BaseOptionsModel):
      raise InvalidModelClassException(
          'Model must inherit anoptions.types.BaseOptionsModel')

    self._model = model

    super().__init__(
        parameters=self._generate_parameter_models(self._model),
        argvs=argvs,
        env_prefix=env_prefix
    )

  @staticmethod
  def _get_types_from_schema(schema: ModelJsonSchema, parameter: str) -> List[Union[str, None]]:
    if parameter not in schema.properties:
      raise Exception(f'Invalid schema parameter: {parameter}')
    p = schema.properties[parameter]
    if 'type' in p:
      return [p['type']]
    if 'anyOf' in p:
      allTypes: List[Dict[str, str]] = p['anyOf']
      return [x['type'] if 'type' in x and x['type'] != 'null' else None for x in allTypes]
    raise Exception(
        f'Invalid schema for parameter "{parameter}": {schema.properties}')

  @staticmethod
  def __get_property_value(
          prop_values: Dict[str, Any],
          value_name: str,
          default: Any = None) -> Any:
    return prop_values[value_name] if value_name in prop_values else default

  @classmethod
  def __get_property_name(cls, prop_values: Dict[str, Any], value_name: str, default: str) -> str:
    return re.sub(
        '[^a-zA-Z0-9]',
        '',
        cls.__get_property_value(
            prop_values=prop_values, value_name=value_name, default=default)
    )

  @classmethod
  def _generate_parameter_models(cls, model: Type[BaseOptionsModel]) -> List[ParameterModel]:
    result: List[ParameterModel] = []
    schema: ModelJsonSchema = ModelJsonSchema(**model.model_json_schema())
    for prop_name, prop_values in schema.properties.items():

      short = cls.__get_property_name(
          prop_values=prop_values, value_name='short_name', default=prop_name)
      long = cls.__get_property_name(
          prop_values=prop_values, value_name='long_name', default=prop_name)
      if (len(short) == 0 or len(long) == 0):
        raise Exception(
            f'Invalid long or short option name for "{prop_name}"')

      types = cls._get_types_from_schema(
          schema=schema, parameter=prop_name)

      result.append(ParameterModel(
          default=cls.__get_property_value(
              prop_values=prop_values, value_name='default'),
          description=cls.__get_property_value(
              prop_values=prop_values, value_name='description'),
          examples=cls.__get_property_value(
              prop_values=prop_values, value_name='examples'),
          is_flag='boolean' in types and None in types,
          is_optional=None in types,
          long_name=long,
          short_name=short[0],
          title=cls.__get_property_value(
              prop_values=prop_values, value_name='title'),
          types=types,
          name=prop_name
      ))
    return result

  def eval(self) -> T:
    return self._model(**self._inputs)
