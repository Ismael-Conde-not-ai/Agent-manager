import unittest

from integrations.argument_validator import MCPArgumentValidator, MCPInputSchemaError


class TestMCPArgumentValidator(unittest.TestCase):

    def setUp(self):
        self.validator = MCPArgumentValidator()

        self.schema = {
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }

    def test_valid_arguments(self):
        self.validator.validate(
            {"a": 10, "b": 20},
            self.schema
        )

    def test_missing_required_argument(self):
        with self.assertRaises(ValueError):
            self.validator.validate(
                {"a": 10},
                self.schema
            )

    def test_invalid_argument_type(self):
        with self.assertRaises(ValueError):
            self.validator.validate(
                {"a": "hello", "b": 20},
                self.schema
            )

    def test_additional_argument(self):
        with self.assertRaises(ValueError):
            self.validator.validate(
                {"a": 10, "b": 20, "c": 30},
                self.schema
            )

    def test_arguments_must_be_dictionary(self):
        with self.assertRaises(ValueError):
            self.validator.validate(
                ["10", "20"],
                self.schema
            )

    def test_invalid_schema(self):
        invalid_schema = {
            "type": "unknown_type"
        }

        with self.assertRaises(MCPInputSchemaError):
            self.validator.validate(
                {"a": 10},
                invalid_schema
            )


if __name__ == "__main__":
    unittest.main()