"""Alice skill: guided morning exercises for an elderly person.

Plain function `handler(event, context)`: works as a Yandex Cloud Function or behind any webhook (see api/alice.py for Vercel).
Each exercise is one reply; the user says "дальше" to move on, so she sets the pace.
Pauses are written as `sil <[ms]>` (Yandex TTS markup); counting aloud sets the rhythm.
Exercises are taken from the video transcript; repetition counts marked (*) are assumptions.
"""
import re

TTS_LIMIT = 1024  # Yandex Dialogs limit for both `text` and `tts`

NUMBERS = ["Раз", "Два", "Три", "Четыре", "Пять", "Шесть", "Семь", "Восемь", "Девять", "Десять"]

NEXT_HINT = "Отлично! Теперь отдохни. Когда будешь готова, скажи «дальше»."


def sil(ms):
    return f"sil <[{ms}]>"


def counted(n, cues, pause_ms):
    """n repetitions: each cue is spoken, followed by a pause (ms), then the rep number."""
    parts = []
    for i in range(n):
        for cue, ms in zip(cues, pause_ms):
            parts.append(f"{cue} {sil(ms)}")
        parts.append(f"{NUMBERS[i]}. {sil(600)}")
    return " ".join(parts)


WELCOME = (
    "Ба, а теперь давай немного позаботимся о себе! Самое время для утренней зарядки. "
    + sil(2000) + " "
    "Она займёт около 10 минут. Будем заниматься спокойно, без спешки, в комфортном для тебя темпе. "
    + sil(2000) + " "
    "Если почувствуешь головокружение, боль или дискомфорт, сразу остановись и отдохни. "
    "Не нужно делать упражнения через силу. "
    + sil(2000) + " "
    "После каждого упражнения я буду делать паузу и ждать, пока ты скажешь «дальше». "
    + sil(1500) + " "
    "Если захочешь ещё раз услышать, как выполнять упражнение, скажи «повтори». "
    + sil(1500) + " "
    "А если захочешь закончить зарядку раньше, просто скажи «хватит». "
    + sil(2000) + " "
    "Для подготовки поставь рядом устойчивый стул. "
    "Лучше, если он будет стоять у стены — так ты сможешь при необходимости опереться. "
    + sil(2000) + " "
    "Ну что, Ба, готова начать? Тогда скажи: «Поехали»!"
)

STEPS = [
    # 1. "Встанька" (video 2:19), 10 reps
    (
        "Упражнение первое, «Встанька». Садись на край стула, спина прямая, стопы плотно на полу. "
        "Встаём, если получается без помощи рук, и садимся, всё медленно. Десять раз. Начали. "
        + counted(10, ["Встаём.", "Садимся."], [2500, 2500])
        + " "
        + NEXT_HINT
    ),
    # 2. "Марш на месте" (video 3:26), right leg (*8 reps)
    (
        "Упражнение второе, «Марш на месте». Вставай боком к спинке стула, слегка придерживайся рукой, "
        "спина прямая. Сначала правая нога. Поднимаем колено выше, чем при ходьбе, держим два счёта и опускаем. "
        "Восемь раз. Начали. "
        + counted(8, ["Поднимаем.", "Держим.", "Опускаем."], [1000, 1500, 1500])
        + " "
        + NEXT_HINT
    ),
    # 3. same, left leg
    (
        "Теперь левая нога. Повернись другим боком к стулу, придерживайся рукой. "
        "Колено вверх, держим два счёта, опускаем. Восемь раз. Начали. "
        + counted(8, ["Поднимаем.", "Держим.", "Опускаем."], [1000, 1500, 1500])
        + " "
        + NEXT_HINT
    ),
    # 4. "Рисование в воздухе" (video 4:35), right foot (*5 circles each way)
    (
        "Упражнение третье, «Рисование в воздухе». Сядь на стул и вытягивай вперёд правую ногу. "
        "Представь, что большой палец — это карандаш, и рисуй им в воздухе круг. "
        "Пять кругов в одну сторону, потом пять в другую. Начали. В одну сторону. "
        + counted(5, ["Круг."], [2000])
        + " Теперь в другую сторону. "
        + counted(5, ["Круг."], [2000])
        + " "
        + NEXT_HINT
    ),
    # 5. same, left foot
    (
        "Теперь то же самое левой ногой. Вытягивай вперёд левую ногу. В одну сторону. "
        + counted(5, ["Круг."], [2000])
        + " Теперь в другую сторону. "
        + counted(5, ["Круг."], [2000])
        + " "
        + NEXT_HINT
    ),
    # 6. "Раскрытие книги" (video 5:30) (*8 reps)
    (
        "Упражнение четвёртое, «Раскрытие книги». Вставай прямо, вытягивай руки перед собой. "
        "На вдохе медленно разведи руки в стороны, раскрывая грудь и сводя лопатки. "
        "На выдохе верни руки вперёд. Восемь раз. Начали. "
        + counted(8, ["Вдох, руки в стороны.", "Выдох, руки вперёд."], [2000, 1500])
        + " "
        + NEXT_HINT
    ),
    # 7. Trunk rotations (not from the video; added by the user's grandmother) (*8 reps)
    (
        "Упражнение пятое, «Повороты туловища». Встань прямо, ноги на ширине плеч, руки на поясе. "
        "Поворачивай корпус медленно, ноги стоят на месте, смотри в сторону поворота. "
        "Вправо, влево, и это один раз. Восемь раз. Начали. "
        + counted(8, ["Вправо.", "Влево."], [1500, 1500])
        + " "
        + NEXT_HINT
    ),
    # 8. Side bends (not from the video; added by the user's grandmother) (*8 reps)
    (
        "Упражнение шестое, «Наклоны». Встань прямо, ноги чуть шире плеч, руки на поясе, рядом стоит стул. "
        "Наклоняйся в сторону медленно и неглубоко, без рывков. Вправо, влево, и это один раз. "
        "Восемь раз. Начали. "
        + counted(8, ["Вправо.", "Влево."], [2000, 2000])
        + " "
        + NEXT_HINT
    ),
    # 9. "Перекат" (video 6:32) (*10 steps)
    (
        "Упражнение седьмое, «Перекат». Пройдись по комнате очень медленно, не шлёпая стопой. "
        "Каждый шаг: пятка, середина, носок. Десять шагов. Начали. "
        + counted(10, ["Пятка.", "Середина.", "Носок."], [800, 800, 400])
        + " "
        + NEXT_HINT
    ),
]

FINAL = "Зарядка закончена, ты молодец! Хорошего дня!"

# Single words only: the command is split into words, so phrases like "не готова" are checked separately below.
STOP_WORDS = {"стоп", "хватит", "закончить", "закончим", "выход", "выйти", "отмена", "остановись", "устала", "устал"}
STOP_PHRASES = ("не готова", "не готов")
NEXT_WORDS = {"дальше", "далее", "готова", "готов", "поехали", "давай", "начнём", "начнем", "начать",
              "продолжай", "продолжить", "следующее", "да", "хорошо", "ок", "угу"}
HELP_WORDS = {"помощь", "помоги", "умеешь"}
REPEAT_PHRASES = ("повтори", "повторить", "ещё раз", "еще раз", "скажи еще раз", "я не услышала", "я не поняла")


def strip_sil(tts):
    return re.sub(r"\s*sil <\[\d+\]>", "", tts).strip()


def reply(event, tts, step, end=False):
    buttons = [] if end else [{"title": t, "hide": True} for t in ("Дальше", "Повтори", "Стоп")]
    return {
        "response": {
            "text": strip_sil(tts),
            "tts": tts,
            "buttons": buttons,
            "end_session": end,
        },
        "session_state": {"step": step},
        "version": event.get("version", "1.0"),
    }


def handler(event, context=None):
    request = event.get("request", {})
    session = event.get("session", {})
    state = (event.get("state") or {}).get("session") or {}
    command = (request.get("command") or "").lower().strip()
    words = set(re.findall(r"\w+", command))

    # step 0 = welcome was played; step k = k-th exercise was played
    step = state.get("step")

    if session.get("new") or step is None:
        return reply(event, WELCOME, 0)

    # Must be checked before NEXT_WORDS, because "не готова" contains the word "готова".
    if words & STOP_WORDS or any(p in command for p in STOP_PHRASES):
        return reply(event, "Хорошо, закончили. Береги себя!", step, end=True)

    if words & HELP_WORDS:
        return reply(event, "Я веду утреннюю зарядку. Скажи «дальше», чтобы продолжить, "
                            "«повтори», чтобы услышать упражнение ещё раз, или «стоп», чтобы закончить.", step)

    if any(p in command for p in REPEAT_PHRASES):
        if step == 0:
            return reply(event, WELCOME, 0)
        return reply(event, STEPS[step - 1], step)

    if words & NEXT_WORDS:
        if step >= len(STEPS):
            return reply(event, FINAL, step, end=True)
        return reply(event, STEPS[step], step + 1)

    return reply(event, "Скажи «дальше», «повтори» или «стоп».", step)
