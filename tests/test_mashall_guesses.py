"""Test _marshall_guesses()."""
import math
import pytest
from wordle_guesses.wordle_guesses import OutputGuessLines, _marshall_guesses


@pytest.fixture(name="guesses")
# explicit name to avoid pylint warnings
# (https://stackoverflow.com/questions/46089480/pytest-fixtures-redefining-name-from-outer-scope-pylint)
def guesses_fixture() -> list[str]:
    """Fixture that returns a list of 10 guesses."""
    return [
        "Booth",
        "Cooth",
        "Dooth",
        "Footh",
        "Gooth",
        "Hooth",
        "Jooth",
        "Kooth",
        "Qooth",
        "Tooth",
    ]


def try_num_lines(guesses_to_try: list[str], num_guesses_per_line: int) -> None:
    """Utility function to check everything for a given list of guesses and the number per line."""
    num_guesses_to_try = len(guesses_to_try)
    guess_lines = _marshall_guesses(guesses_to_try, num_guesses_per_line)

    assert len(guess_lines) == math.ceil(num_guesses_to_try / num_guesses_per_line)
    assert len(guess_lines[0]) == num_guesses_per_line
    if num_guesses_to_try % num_guesses_per_line == 0:
        assert len(guess_lines[-1]) == num_guesses_per_line
    else:
        assert len(guess_lines[-1]) == num_guesses_to_try % num_guesses_per_line


def test_marshall_guesses(guesses) -> None:
    """Test marshall_guesses()."""
    guess_lines: OutputGuessLines
    guess_lines = _marshall_guesses([], 5)
    assert len(guess_lines) == 0

    assert len(guesses) == 10
    try_num_lines(guesses, 3)
    try_num_lines(guesses, 4)
    try_num_lines(guesses, 5)
