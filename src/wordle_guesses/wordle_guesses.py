"""Given a template and a set of letters to ignore, print out a list of potential Wordle guesses."""

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from enum import Enum


# Code snarfed from https://stackoverflow.com/questions/7001144/range-over-character-in-python
def char_range(start_char, end_char):
    """Generates the characters from `start_char` to `end_char`, inclusive."""
    for char in range(ord(start_char), ord(end_char) + 1):
        yield chr(char)


BLANK_CHAR = "_"
CHANGE_CHAR = "."

EXCLUDE_OPT = "-e"
EXCLUDE_OPT_LONG = "-exclude"
INCLUDE_OPT = "-i"
INCLUDE_OPT_LONG = "-include"
CASE_OPT = "-c"
CASE_OPT_LONG = "-case"
NUM_OPT = "-n"
NUM_OPT_LONG = "-num_guesses"

CASE_OPT_TITLE = "title"
CASE_OPT_UPPER = "upper"
CASE_OPT_LOWER = "lower"

DEFAULT_NUM_GUESSES_PER_LINE = 5


class OutputCase(Enum):
    """Casing of output of potential Wordle guesses."""

    TITLE = CASE_OPT_TITLE
    UPPER = CASE_OPT_UPPER
    LOWER = CASE_OPT_LOWER

    def transform(self, guess: str) -> str:
        """Given a guess, return the transformation corresponding to this OutputCase."""
        return _TRANSFORMERS[self](guess)


_TRANSFORMERS = {
    # We don't use str.title() to avoid output like "M_Dam".
    # NB: Assumes that the BLANK_CHAR is caseless.
    OutputCase.TITLE: lambda guess: guess[0].upper() + guess[1:].lower(),
    OutputCase.LOWER: lambda guess: guess.lower(),
    OutputCase.UPPER: lambda guess: guess.upper(),
}


@dataclass(frozen=True)
class CommandArgs:
    """Class to represent the results of parsing the command line arguments."""

    template: str
    excluded_letters: set[str]
    included_letters: set[str]
    output_case: OutputCase
    num_guesses_per_line: int


def parse_args(argv: list[str]) -> CommandArgs:
    """Given command-line arguments, return an 'Args' object."""
    parser = argparse.ArgumentParser(
        description=f"""\
            A program you can use to list out candidate Wordle guesses.
            You specify the pattern for the candidate guesses using a template where a '{CHANGE_CHAR}' indicates
            the letter to be changed to generate the candidate guesses. The program will iterate through
            the alphabet, substituting the '{CHANGE_CHAR}' with each letter to generate a guess.
            You can specify a list of letters to exclude when generating the candidate guesses; typically,
            you would do this for the letters which Wordle has indicated aren't in the answer.
            Alternatively, instead of iterating through the alphabet, you can specify the set of letters
            to include when making guesses.""",
        epilog=f"""\
            For example: %(prog)s {EXCLUDE_OPT} risengycuk
            {CASE_OPT} {CASE_OPT_LOWER} {NUM_OPT} 4 {CHANGE_CHAR}a{BLANK_CHAR}am""",
    )
    parser.add_argument(
        "template",
        help=f"""\
            template is a 5-character sequence composed of letters,
            any number of the character '{BLANK_CHAR}',
            and a single instance of the character '{CHANGE_CHAR}' ('{CHANGE_CHAR}a{BLANK_CHAR}am', for example)""",
    )
    exclude_include_group = parser.add_mutually_exclusive_group()
    exclude_include_group.add_argument(
        EXCLUDE_OPT,
        EXCLUDE_OPT_LONG,
        required=False,
        nargs=1,
        metavar="excluded_letters",
        help="specify list of letters to exclude when generating candidate guesses",
    )
    exclude_include_group.add_argument(
        INCLUDE_OPT,
        INCLUDE_OPT_LONG,
        required=False,
        nargs=1,
        metavar="included_letters",
        help="specify explicit list of letters to include when generating candidate guesses",
    )
    parser.add_argument(
        CASE_OPT,
        CASE_OPT_LONG,
        choices=[CASE_OPT_TITLE, CASE_OPT_UPPER, CASE_OPT_LOWER],
        required=False,
        help="specify wheter the candidate guesses are rendered in title case (the default), upper case, or lower case.",
    )
    parser.add_argument(
        NUM_OPT,
        NUM_OPT_LONG,
        type=int,
        required=False,
        help=f"""specify the number of guesses per line of output.
        The default is {DEFAULT_NUM_GUESSES_PER_LINE}.""",
    )

    def usage() -> None:
        sys.exit(parser.format_help())

    args = parser.parse_args(argv)
    logging.debug("args=%s", args)

    # extract and validate required template argument
    template = args.template
    template = template.upper()
    logging.debug("template=%s", template)

    if len(template) != 5:
        usage()
    template_re = re.compile(f"[A-Z{BLANK_CHAR}]*\\{CHANGE_CHAR}[A-Z{BLANK_CHAR}]*")
    template_match = template_re.fullmatch(template)
    if template_match is None:
        usage()

    # built set of letters to exclude from iteration
    excluded_letters: set[str] = set()
    if args.e is not None:
        excluded_arg = args.e[0].upper()
        if not excluded_arg.isalpha():
            usage()
        excluded_letters = set(excluded_arg)
    logging.debug("excluded_letters=%s", excluded_letters)

    # built set of letters to include in iteration
    included_letters: set[str] = set()
    if args.i is not None:
        included_arg = args.i[0].upper()
        if not included_arg.isalpha():
            usage()
        included_letters = set(included_arg)
    logging.debug("included_letters=%s", included_letters)

    # determine the desired output case
    output_case = OutputCase.TITLE
    if args.c is not None:
        output_case = OutputCase(args.c)
    logging.debug("case_selection=%s", output_case)

    # determine the desired number of guesses per line of output
    num_guesses = DEFAULT_NUM_GUESSES_PER_LINE
    if args.n is not None:
        num_guesses = args.n
    logging.debug("num_guesses=%s", num_guesses)

    return CommandArgs(
        template=template,
        excluded_letters=excluded_letters,
        included_letters=included_letters,
        output_case=output_case,
        num_guesses_per_line=num_guesses,
    )


def list_guesses(
    template: str, excluded_letters: set[str], included_letters: set[str]
) -> list[str]:
    """Given 'template' and sets of ignored letters to exclude ('excluded_letters')
    or include ('included_letters'), return a list of potential Wordle guesses.
    All arguments are assumed to be all uppercase. If both 'excluded_letters' and
    'included_letters' are non-empty, the latter is used."""
    if template is None:
        raise ValueError("No template specified")
    # if not template.isalpha():
    #     raise ValueError(f"template '{template}' must be letters only")
    if len(template) != 5:
        raise ValueError(f"template '{template}' must be 5 letters in length")

    parts = template.split(CHANGE_CHAR)
    if len(parts) == 1:
        raise ValueError(f"template '{template}' missing '{CHANGE_CHAR}'")

    front_part = parts[0]
    back_part = parts[1]
    if not front_part.isalpha or not back_part.isalpha:
        raise ValueError(
            f"template '{template}' has non-letter characters other than '{CHANGE_CHAR}'"
        )

    bad_letters = [x for x in excluded_letters if not x.isalpha()]
    if len(bad_letters) > 0:
        raise ValueError("excluded_letters contains one or more non-letter characters")
    bad_letters = [x for x in included_letters if not x.isalpha()]
    if len(bad_letters) > 0:
        raise ValueError("included_letters contains one or more non-letter characters")

    guesses: list[str]
    if len(included_letters) == 0:
        guesses = [
            letter.join([front_part, back_part])
            for letter in char_range("A", "Z")
            if letter not in excluded_letters
        ]
    else:
        guesses = [letter.join([front_part, back_part]) for letter in included_letters]

    return guesses


# type representing lines of guesses to output
OutputGuessLines = list[list[str]]


def _marshall_guesses(guesses: list[str], num_words_per_line: int) -> OutputGuessLines:
    """Given a list of potential Wordle guesses and an output case, return a GuessLines representing lines of guesses to output."""
    lines: OutputGuessLines = []

    current_line: list[str] = []
    for guess in guesses:
        if len(current_line) == num_words_per_line:
            lines.append(current_line)
            current_line = []
        current_line.append(guess)

    if len(current_line) > 0:
        lines.append(current_line)

    return lines


def _print_guesses(guesses: OutputGuessLines) -> None:
    """Given a list of potential Wordle guesses and an output case, print them out."""
    for guess_list in guesses:
        print("\t".join(guess_list))


def main() -> None:
    """Simple main()"""
    logging.basicConfig(level=logging.ERROR)

    args = parse_args(sys.argv[1:])

    guesses = list_guesses(args.template, args.excluded_letters, args.included_letters)

    guesses = map(args.output_case.transform, guesses)

    guess_lines = _marshall_guesses(guesses, args.num_guesses_per_line)
    _print_guesses(guess_lines)


if __name__ == "__main__":
    main()
