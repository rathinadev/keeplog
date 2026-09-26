from keeplog.capture import _clean_output, _strip_ansi


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


def test_strip_ansi_osc_terminated_by_st():
    assert _strip_ansi("\x1b]0;title\x1b\\hi\x1b]133;D;0\x1b\\") == "hi"


def test_strip_ansi_private_csi_and_two_byte_escapes():
    assert _strip_ansi("\x1b=\x1b[>c\x1b[>qok\x1b>") == "ok"


def test_clean_output_removes_zsh_prompt_sp():
    assert _clean_output(b"hello\r\n\x1b[7m%\x1b[27m" + b" " * 60 + b"\r \r") == "hello\r\n"


def test_clean_output_zsh_prompt_sp_after_partial_line():
    assert _clean_output(b"foo%" + b" " * 60 + b"\r \r") == "foo"


def test_clean_output_removes_leading_carriage_return():
    assert _clean_output(b"\rhello\r\n") == "hello\r\n"
    assert _clean_output(b"\r\nblank first line") == "\r\nblank first line"


def test_clean_output_leaves_normal_text():
    assert _clean_output(b"50% done\r\n") == "50% done\r\n"
