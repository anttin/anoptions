import os
from typing import Dict, Optional, Union


class Env:

  @staticmethod
  def get(varname, default: Optional[str] = None) -> Union[str, None]:
    r = os.getenv(varname)
    return r if r is not None else default

  @classmethod
  def get_kv_from_env(cls, dict_of_keys: Dict[str, str]) -> Dict[str, str]:
    """
    Parameters:
      - dict_of_keys: dictionary, where dict-key is the environment variable name
                      and dict-value is the name of the config variable we want
                      to set with the env-value

    Returns:
      - dictionary, where dict-key is the config variable and dict-value is the value
    """

    result: Dict[str, str] = {}

    for k, var_name in dict_of_keys.items():
      v = cls.get(k)

      if v is not None:
        result[var_name] = v

    return result
