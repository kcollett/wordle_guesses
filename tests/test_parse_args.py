"""Test parse_args()"""
import pytest

from wordle_guesses.wordle_guesses import (
    CASE_OPT,
    CHANGE_CHAR,
    EXCLUDE_OPT,
    EXCLUDE_OPT_LONG,
    INCLUDE_OPT,
    INCLUDE_OPT_LONG,
    CASE_OPT_LOWER,
    CASE_OPT_TITLE,
    CASE_OPT_UPPER,
    CommandArgs,
    OutputCase,
    parse_args,
)


@pytest.fixture(name="template")
# explicit name to avoid pylint warnings
# (https://stackoverflow.com/questions/46089480/pytest-fixtures-redefining-name-from-outer-scope-pylint)
def template_fixture() -> str:
    """Fixture that returns a valid template."""
    return f"XYZ{CHANGE_CHAR}Y"


def test_parse_args_bad_basic(template) -> None:
    """Test parse_args() with bad option or -h option."""
    with pytest.raises(SystemExit) as _:
        parse_args(["-badarg", template])  # invalid option
    with pytest.raises(SystemExit) as _:
        parse_args(["-h", template])  # help option


def test_parse_args_bad_template(template) -> None:
    """Test parse_args() with missing or incorrect template."""
    with pytest.raises(SystemExit) as _:
        parse_args([])  # missing template
    with pytest.raises(SystemExit) as _:
        parse_args(["ABCDE"])  # template without CHANGE_CHAR
    with pytest.raises(SystemExit) as _:
        parse_args([f"A1{CHANGE_CHAR}DE"])  # invalid character in template
    with pytest.raises(SystemExit) as _:
        parse_args([template + "A"])  # template too long


def test_parse_args_bad_exclude_include(template) -> None:
    """Test parse_args() with bad exclude or include arguments."""
    with pytest.raises(SystemExit) as _:
        parse_args([EXCLUDE_OPT, template])  # exclude without chars
    with pytest.raises(SystemExit) as _:
        parse_args([EXCLUDE_OPT, "a1", template])  # exclude with invalid chars
    with pytest.raises(SystemExit) as _:
        parse_args([INCLUDE_OPT, template])  # include without chars
    with pytest.raises(SystemExit) as _:
        parse_args([INCLUDE_OPT, "a1", template])  # include with invalid chars
    with pytest.raises(SystemExit) as _:
        parse_args(
            [EXCLUDE_OPT, "a", INCLUDE_OPT, "b", template]
        )  # both include and exclude opts


def test_parse_args_bad_case(template) -> None:
    """Test parse_args() with a bad case argument."""
    with pytest.raises(SystemExit) as _:
        parse_args([CASE_OPT, template])  # option without case
    with pytest.raises(SystemExit) as _:
        parse_args([CASE_OPT, "snake", template])  # invalid case


def test_parse_args_template_only(template) -> None:
    """Test parse_args() with only a template argument."""
    command_args = parse_args([template])
    assert command_args.template == template


def test_parse_args_exclude(template) -> None:
    """Test parse_args() with excluded letters."""
    excluded_letters = "ABCDE"

    command_args: CommandArgs
    command_args = parse_args([EXCLUDE_OPT, excluded_letters, template])
    assert command_args.excluded_letters == set(excluded_letters)
    command_args = parse_args([EXCLUDE_OPT_LONG, excluded_letters, template])
    assert command_args.excluded_letters == set(excluded_letters)


def test_parse_args_include(template) -> None:
    """Test parse_args() with included letters."""
    included_letters = "ABCDE"

    command_args: CommandArgs
    command_args = parse_args([INCLUDE_OPT, included_letters, template])
    assert command_args.included_letters == set(included_letters)
    command_args = parse_args([INCLUDE_OPT_LONG, included_letters, template])
    assert command_args.included_letters == set(included_letters)


def test_parse_args_case(template) -> None:
    """Test parse_args() with output case specification."""
    command_args: CommandArgs
    command_args = parse_args([template])  # TITLE should be the default
    assert command_args.output_case == OutputCase.TITLE
    command_args = parse_args([CASE_OPT, CASE_OPT_TITLE, template])
    assert command_args.output_case == OutputCase.TITLE
    command_args = parse_args([CASE_OPT, CASE_OPT_LOWER, template])
    assert command_args.output_case == OutputCase.LOWER
    command_args = parse_args([CASE_OPT, CASE_OPT_UPPER, template])
    assert command_args.output_case == OutputCase.UPPER
