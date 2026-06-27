from keeplog.capture import _strip_ansi


def test_strip_ansi_colors():
    assert _strip_ansi("\x1b[32mhello\x1b[0m") == "hello"


def test_strip_ansi_cursor():
    assert _strip_ansi("line1\x1b[?25l") == "line1"


def test_strip_ansi_osc():
    assert _strip_ansi("foo\x1b]0;title\x07bar") == "foobar"


def test_strip_ansi_mixed():
    raw = "\x1b[1;34mλ\x1b[0m \x1b[32mls\x1b[0m"
    assert _strip_ansi(raw) == "λ ls"


def test_strip_ansi_plain_text():
    assert _strip_ansi("hello world") == "hello world"


def test_strip_ansi_empty():
    assert _strip_ansi("") == ""
