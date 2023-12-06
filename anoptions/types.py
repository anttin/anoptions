from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, ConfigDict  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods


class BaseOptionsModel(BaseModel):
  pass


class ParameterModel(BaseModel):
  default: Any
  description: Optional[str] = None
  examples: Optional[List[str]] = None
  is_flag: bool
  is_optional: bool
  long_name: str
  name: str
  short_name: str
  title: str
  types: List[Union[str, None]]


class ModelJsonSchema(BaseModel):
  properties: Dict[str, Any]


class LookupVariables(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)

  shortopts: str
  longopts: List[str]
  lookup_option: Dict[str, ParameterModel]
  lookup_name: Dict[str, ParameterModel]
