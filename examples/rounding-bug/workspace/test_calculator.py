from decimal import Decimal
import unittest

from calculator import money


class MoneyTests(unittest.TestCase):
    def test_half_cent_rounds_up(self):
        self.assertEqual(money("1.005"), Decimal("1.01"))

    def test_exact_value_is_preserved(self):
        self.assertEqual(money("12.30"), Decimal("12.30"))

    def test_negative_half_cent_rounds_away_from_zero(self):
        self.assertEqual(money("-2.675"), Decimal("-2.68"))


if __name__ == "__main__":
    unittest.main()
