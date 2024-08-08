from shared.validation_result import ValidationResult


class BaseRequest():
    def validate(self) -> ValidationResult:
        pass
