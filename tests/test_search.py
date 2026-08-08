from keeplog import search


def test_has_fzf_true(monkeypatch):
    monkeypatch.setattr(search.shutil, "which", lambda name: "/usr/bin/fzf")
    assert search._has_fzf() is True


def test_has_fzf_false(monkeypatch):
    monkeypatch.setattr(search.shutil, "which", lambda name: None)
    assert search._has_fzf() is False


def test_search_interactive_no_results(monkeypatch, capsys):
    monkeypatch.setattr(search, "db_search", lambda query, **kw: [])
    search.search_interactive("nothing")
    out = capsys.readouterr().out
    assert "No results found" in out


def test_search_interactive_falls_back_without_fzf(monkeypatch, capsys):
    monkeypatch.setattr(
        search, "db_search",
        lambda query, **kw: [{"id": 1, "command": "ls -la", "output_preview": "file1\nfile2"}],
    )
    monkeypatch.setattr(search, "_has_fzf", lambda: False)

    search.search_interactive("ls")

    out = capsys.readouterr().out
    assert "[1] ls -la" in out
    assert "file1 | file2" in out


def test_print_results_handles_missing_preview(capsys):
    search._print_results([{"id": 2, "command": "pwd", "output_preview": None}])
    out = capsys.readouterr().out
    assert "[2] pwd" in out
