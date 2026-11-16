import json
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

import lambda_function


class TestVisitorCounter(unittest.TestCase):
    def test_increments_and_returns_count(self):
        fake_table = MagicMock()
        fake_table.update_item.return_value = {"Attributes": {"count": Decimal("42")}}

        with patch.object(lambda_function, "_get_table", return_value=fake_table):
            response = lambda_function.lambda_handler({}, None)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(json.loads(response["body"]), {"count": 42})

        # The counter item and the atomic ADD update were used
        kwargs = fake_table.update_item.call_args.kwargs
        self.assertEqual(kwargs["Key"], {"id": "visits"})
        self.assertEqual(kwargs["ExpressionAttributeValues"], {":inc": 1})

    def test_response_is_json(self):
        fake_table = MagicMock()
        fake_table.update_item.return_value = {"Attributes": {"count": Decimal("1")}}

        with patch.object(lambda_function, "_get_table", return_value=fake_table):
            response = lambda_function.lambda_handler({}, None)

        self.assertEqual(response["headers"]["Content-Type"], "application/json")

    def test_returns_500_when_dynamodb_fails(self):
        fake_table = MagicMock()
        fake_table.update_item.side_effect = Exception("DynamoDB unavailable")

        with patch.object(lambda_function, "_get_table", return_value=fake_table):
            response = lambda_function.lambda_handler({}, None)

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))


if __name__ == "__main__":
    unittest.main()
