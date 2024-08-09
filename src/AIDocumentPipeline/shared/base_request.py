from shared.validation_result import ValidationResult


class BaseRequest():
    """Defines the base class for requests passed to a workflow operation, including orchestration and activity functions."""

    def validate(self) -> ValidationResult:
        """Validates the request object and returns a `ValidationResult` instance containing any validation messages."""
        pass
