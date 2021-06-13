from typing import List, Tuple
from visli import slices
import pytest


@pytest.mark.parametrize("overall_length, default_slice_lenght, result", [
    (60, 60, [(0, 60)]),
    (100, 50, [(0, 50), (20, 50), (40, 60)]),
])
def test_visli__slices__1(
    overall_length: int,
    default_slice_lenght: int,
    result: List[Tuple[int, int]]
):
    """It slices with overlap of 30 s, last slice is up to 1.5 times bigger."""
    assert list(slices(overall_length, default_slice_lenght)) == result
