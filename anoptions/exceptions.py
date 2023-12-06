class DuplicateOptionException(Exception):
  pass


class InvalidModelClassException(Exception):
  pass


class RequiredParameterMissingException(Exception):
  def __init__(self, *args: object, parameter: str) -> None:
    super().__init__(*args)
    self.parameter = parameter
