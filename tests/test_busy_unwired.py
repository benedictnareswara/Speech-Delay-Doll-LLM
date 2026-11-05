"""DFPlayer sink with the BUSY line not wired (the reference build).

With no BUSY wire the sink must time playback straight from the manifest,
without first waiting out BUSY_ASSERT_TIMEOUT_S for a pin that will never move.
"""

from types import SimpleNamespace

import speechllm_device.output.dfplayer_sink as sink_mod
from speechllm_device.hardware.gpio import MockBusyPin, open_busy_pin
from speechllm_device.output.dfplayer_sink import DFPlayerSink


class _FakePlayer:
    def __init__(self):
        self.played = []

    def play(self, folder, track):
        self.played.append((folder, track))

    def close(self):
        pass


def _manifest():
    track = SimpleNamespace(phoneme="MA", variant=0, duration_ms=3200)
    return SimpleNamespace(tracks=[track], ui_tracks={}, track_number=lambda p, v: 6)


def test_force_mock_returns_unavailable_pin():
    pin = open_busy_pin(force_mock=True)
    assert isinstance(pin, MockBusyPin)
    assert pin.available is False


def test_unwired_sleeps_manifest_duration_only(monkeypatch):
    sleeps = []
    monkeypatch.setattr(sink_mod.time, "sleep", lambda s: sleeps.append(s))

    player = _FakePlayer()
    sink = DFPlayerSink(player, _manifest(), MockBusyPin())
    response = SimpleNamespace(
        bank_phoneme="MA", bank_variant=0, phoneme="MA", text="Mama!", source="test"
    )
    sink.speak(response)

    assert player.played == [(1, 6)]
    # One sleep for the track length, no BUSY polling beforehand.
    assert sleeps == [3.2]


def test_busy_wired_defaults_to_false(monkeypatch):
    monkeypatch.delenv("DFPLAYER_BUSY_WIRED", raising=False)
    from speechllm_core.settings import Settings

    assert Settings().dfplayer_busy_wired is False
    monkeypatch.setenv("DFPLAYER_BUSY_WIRED", "1")
    assert Settings().dfplayer_busy_wired is True
