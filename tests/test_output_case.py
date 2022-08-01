"""Test OutputCase"""
from wordle_guesses.wordle_guesses import CASE_OPT_LOWER, CASE_OPT_TITLE, CASE_OPT_UPPER, OutputCase

def test_init() -> None:
    """Test OutputCase __init__()."""
    test_oc: OutputCase

    test_oc = OutputCase(CASE_OPT_TITLE)
    assert test_oc == OutputCase.TITLE
    test_oc = OutputCase(CASE_OPT_LOWER)
    assert test_oc == OutputCase.LOWER
    test_oc = OutputCase(CASE_OPT_UPPER)
    assert test_oc == OutputCase.UPPER

def test_transform() -> None:
    """Test OutputCase transform()."""
    assert "ab_de" == OutputCase.LOWER.transform("AB_DE")
    assert "ab_de" == OutputCase.LOWER.transform("ab_de")

    assert "AB_DE" == OutputCase.UPPER.transform("ab_de")
    assert "AB_DE" == OutputCase.UPPER.transform("AB_DE")

    assert "Ab_de" == OutputCase.TITLE.transform("AB_DE")
    assert "Ab_de" == OutputCase.TITLE.transform("ab_de")
    assert "Ab_de" == OutputCase.TITLE.transform("Ab_de")
    assert "_bcde" == OutputCase.TITLE.transform("_BCDE")
    assert "_bcde" == OutputCase.TITLE.transform("_bcde")
