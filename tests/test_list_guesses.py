"""Test list_guesses()"""
import pytest
from wordle_guesses.wordle_guesses import BLANK_CHAR, CHANGE_CHAR, list_guesses

# build template of _A@AM
TEST_TEMPLATE_PREFIX = f"{BLANK_CHAR}A"
TEST_TEMPLATE_SUFFIX = "AM"
TEST_TEMPLATE = f"{TEST_TEMPLATE_PREFIX}{CHANGE_CHAR}{TEST_TEMPLATE_SUFFIX}"

NUM_ALPHA_LETTERS = 26


def test_list_guesses_empty() -> None:
    """Test list_guesses() with empty exclude and include."""
    guesses = list_guesses(
        TEST_TEMPLATE,
        set(),
        set(),
    )
    assert len(guesses) == NUM_ALPHA_LETTERS
    assert guesses[0] == f"{TEST_TEMPLATE_PREFIX}A{TEST_TEMPLATE_SUFFIX}"
    assert guesses[1] == f"{TEST_TEMPLATE_PREFIX}B{TEST_TEMPLATE_SUFFIX}"
    assert guesses[25] == f"{TEST_TEMPLATE_PREFIX}Z{TEST_TEMPLATE_SUFFIX}"
    guess_set = set(guesses)
    assert len(guess_set) == NUM_ALPHA_LETTERS

def test_list_guesses_bad_template() -> None:
    """Test parse_args() with bad option or -h option."""
    with pytest.raises(ValueError) as _:
        list_guesses(None, set(), set())  # no template
    with pytest.raises(ValueError) as _:
        list_guesses("", set(), set())  # empty template
    with pytest.raises(ValueError) as _:
        list_guesses("ab1de", set(), set())  # template with non-alpha character
    with pytest.raises(ValueError) as _:
        list_guesses("abcde", set(), set())  # template w/o CHANGE_CHAR
    with pytest.raises(ValueError) as _:
        list_guesses("ab.de", set(["a", "1"]), set())  # bad letter in excluded_letters
    with pytest.raises(ValueError) as _:
        list_guesses("ab.de", set(), set(["a", "1"]))  # bad letter in included_letters

def test_list_guesses_exclude() -> None:
    """Test list_guesses() with excluded letters."""
    excluded_letters_list = ["D", "L", "X"]
    excluded_letters = set(excluded_letters_list)
    guesses = list_guesses(
        TEST_TEMPLATE,
        excluded_letters,
        set(),
    )
    assert len(guesses) == NUM_ALPHA_LETTERS - len(excluded_letters)
    guess_set = set(guesses)
    assert len(guess_set) == NUM_ALPHA_LETTERS - len(excluded_letters)
    for letter in excluded_letters_list:
        excluded_candidate = f"{TEST_TEMPLATE_PREFIX}{letter}{TEST_TEMPLATE_SUFFIX}"
        assert excluded_candidate not in guess_set

def test_list_guesses_include() -> None:
    """Test list_guesses() with included letters."""
    included_letters_list = ["D", "L", "X"]
    included_letters = set(included_letters_list)
    guesses = list_guesses(
        TEST_TEMPLATE,
        set(),
        included_letters,
    )
    assert len(guesses) == len(included_letters)
    guess_set = set(guesses)
    assert len(guess_set) == len(included_letters)
    for letter in included_letters_list:
        included_candidate = f"{TEST_TEMPLATE_PREFIX}{letter}{TEST_TEMPLATE_SUFFIX}"
        assert included_candidate in guess_set
