from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


from core.exceptions import MCPCommunicationError, ValidationError


class MCPArgumentValidationError(ValidationError):
    """Los argumentos enviados no cumplen el esquema de la herramienta MCP."""


class MCPInputSchemaError(ValidationError):
    """El esquema proporcionado por el servidor MCP es inválido."""


class MCPToolExecutionError(MCPCommunicationError):
    """La herramienta MCP no pudo ejecutarse correctamente."""

class MCPArgumentValidator:
    """
    Validates arguments against an MCP tool input schema.
    """

    def validate(
        self,
        arguments: dict,
        input_schema: dict
    ) -> None:
        """
        Raises ValueError when arguments are invalid.
        """

        if not isinstance(arguments, dict):
            raise ValueError(  # noqa: TRY004
                "Tool arguments must be a dictionary."
            )

        if not isinstance(input_schema, dict):
            raise ValueError(  # noqa: TRY004
                "MCP input schema must be a dictionary."
            )

        try:
            Draft202012Validator.check_schema(input_schema)

            validator = Draft202012Validator(input_schema)

            errors = sorted(
                validator.iter_errors(arguments),
                key=lambda error: list(error.path)
            )

            if errors:
                messages = [
                    error.message
                    for error in errors
                ]

                raise MCPArgumentValidationError(
                    "Invalid MCP tool arguments: "
                    + "; ".join(messages)
                )

        except SchemaError as error:
            raise MCPInputSchemaError(
                f"Invalid MCP input schema: {error.message}"
            ) from error