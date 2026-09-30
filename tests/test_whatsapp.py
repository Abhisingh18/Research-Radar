from research_radar import whatsapp


def _clear(monkeypatch):
    for var in ("CALLMEBOT_PHONE", "CALLMEBOT_APIKEY"):
        monkeypatch.delenv(var, raising=False)


def test_not_configured_when_nothing_set(monkeypatch):
    _clear(monkeypatch)
    assert whatsapp.is_configured() is False


def test_not_configured_when_only_phone_set(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("CALLMEBOT_PHONE", "919648531091")
    assert whatsapp.is_configured() is False


def test_configured_with_both_vars(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("CALLMEBOT_PHONE", "919648531091")
    monkeypatch.setenv("CALLMEBOT_APIKEY", "123456")
    assert whatsapp.is_configured() is True


def test_send_returns_false_when_not_configured(monkeypatch):
    _clear(monkeypatch)
    assert whatsapp.send("hello") is False
