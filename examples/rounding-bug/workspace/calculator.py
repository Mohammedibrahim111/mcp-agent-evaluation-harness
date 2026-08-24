"""Golden solution for decimal currency rounding."""

from decimal import Decimal, ROUND_HALF_UP


def money(value: str | Decimal) -> Decimal:
    """Round a decimal value to cents using commercial half-up behavior."""

    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
