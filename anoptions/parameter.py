from typing import Any, Optional, Callable, List, Union


# pylint: disable=too-many-instance-attributes
class Parameter:

  # pylint: disable=too-many-arguments
  def __init__(self,
               name: str,
               func: Callable[..., Any],
               var_name: Optional[str] = None,
               short_name: Optional[str] = None,
               default: Optional[Any] = None,
               always_include: Optional[bool] = False,
               description: Optional[str] = None,
               examples: Optional[List[str]] = None,
               required: bool = False
               ):
    """
    Parameters:
      - name: Parameter long name (--name),
      - func: Function that converts the commandline string input to the desired type.
      - var_name: Variable name for the parameter in Options-objects eval-output.
      - short_name: Parameter short name (-s),
      _ default: Default value if no input is given,
      - always_include: Is set to True, this value is always present in evaluation
                        output even if no value was given and no default value is
                        defined. In that case, the value will be None.
      - description: Text description.
      - examples: List of example values.
      - required: If True, the evaluation will fail the evaluation if no value is
                  inputted for this parameter.
    """

    super().__init__()

    self._name = name
    # replace the regular bool function with one in Parameter
    # to ensure that we get values evaluated correctly
    self._func = Parameter.bool if func is bool else func
    self._var_name = var_name if var_name else name
    self._short_name = short_name[0] if short_name is not None and len(
        short_name) > 0 else name[0]
    self._default = default if not self.is_parameter_a_flag else False
    self._always_include = always_include
    self._description = description
    self._examples = examples
    self._required = required

  @property
  def name(self) -> str:
    return self._name

  @property
  def func(self) -> Callable[..., Any]:
    return self._func

  @func.setter
  def func(self, value: Callable) -> None:
    self._func = value

  @property
  def var_name(self) -> str:
    return self._var_name

  @property
  def short_name(self) -> str:
    return self._short_name

  @property
  def default(self) -> Any:
    return self._default

  @property
  def always_include(self) -> Any:
    return self._always_include

  @always_include.setter
  def always_include(self, value: bool) -> None:
    self._always_include = value

  @property
  def description(self) -> Optional[str]:
    return self._description

  @property
  def examples(self) -> Optional[List[str]]:
    return self._examples

  @property
  def title(self) -> str:
    return self._name

  @property
  def is_parameter_a_flag(self) -> bool:
    return self.is_flag(self._func)

  @property
  def is_optional(self) -> bool:
    return not self._required

  @property
  def types(self) -> List[Union[str, None]]:
    result: List[Union[str, None]] = [self.func.__name__]
    if self.is_optional:
      result.append(None)
    return result

  @staticmethod
  def dummy(arg):
    return arg

  @staticmethod
  def flag(*argv):
    return True

  @staticmethod
  def _eval_bool(value: Any) -> bool:
    if isinstance(value, bool):
      return value
    if isinstance(value, int):
      return value == 1
    if isinstance(value, str):
      return value.upper() in ("1", "TRUE")
    return bool(value)

  @classmethod
  def bool(cls, *argv):
    # if no params are given, act like flag()
    if len(argv) < 1:
      return cls.flag(*argv)

    # if this is a flag from getopt, the value is str and len=0
    if isinstance(argv[0], str) and len(argv[0]) == 0:
      return True

    # else we evaluate the variable contents
    return cls._eval_bool(argv[0])

  @classmethod
  def is_flag(cls, f: Callable):
    return f in (cls.flag, cls.bool)
