"""Golden reference solution retained outside the candidate workspace."""

from decimal import Decimal, ROUND_HALF_UP


def money(value: str | Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
