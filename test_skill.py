"""Local checks for the skill. Run: python3 test_index.py"""
import re

import skill as index


def make_event(command="", new=False, step=None):
    state = {"session": {"step": step}} if step is not None else {}
    return {
        "request": {"command": command, "type": "SimpleUtterance"},
        "session": {"new": new, "session_id": "test"},
        "state": state,
        "version": "1.0",
    }


def say(command, state_step):
    return index.handler(make_event(command, step=state_step))


def test_new_session_plays_welcome():
    r = index.handler(make_event(new=True))
    assert r["response"]["end_session"] is False
    assert "поехали" in r["response"]["text"]
    assert r["session_state"] == {"step": 0}


def test_full_dialog_reaches_end():
    r = index.handler(make_event(new=True))
    step = r["session_state"]["step"]
    for _ in range(len(index.STEPS)):
        r = say("дальше", step)
        assert r["response"]["end_session"] is False
        step = r["session_state"]["step"]
    assert step == len(index.STEPS)
    r = say("дальше", step)
    assert r["response"]["end_session"] is True


def test_length_limits():
    texts = [index.WELCOME, index.FINAL] + index.STEPS
    for tts in texts:
        assert len(tts) <= index.TTS_LIMIT - 24, f"tts too long ({len(tts)}): {tts[:40]}"
        assert len(index.strip_sil(tts)) <= index.TTS_LIMIT


def test_repeat_returns_same_step():
    r = say("повтори", 3)
    assert r["response"]["tts"] == index.STEPS[2]
    assert r["session_state"] == {"step": 3}


def test_stop_ends_session():
    r = say("стоп", 2)
    assert r["response"]["end_session"] is True


def test_unknown_command_reprompts():
    r = say("расскажи анекдот", 2)
    assert r["response"]["end_session"] is False
    assert r["session_state"] == {"step": 2}


def test_lost_state_restarts_from_welcome():
    r = index.handler(make_event("дальше"))
    assert r["session_state"] == {"step": 0}


def estimate_seconds(tts):
    """Very rough: pauses + ~15 characters of speech per second (an assumption, not measured)."""
    pauses = sum(int(ms) for ms in re.findall(r"sil <\[(\d+)\]>", tts)) / 1000
    speech = len(index.strip_sil(tts)) / 15
    return pauses + speech


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("OK  ", t.__name__)
    total = 0
    for i, tts in enumerate(index.STEPS, 1):
        sec = estimate_seconds(tts)
        total += sec
        print(f"step {i}: {len(tts)} chars, ~{sec:.0f} s")
    print(f"estimated total: ~{total / 60:.1f} min (rough estimate)")
