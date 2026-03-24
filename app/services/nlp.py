import json
import re
from collections import Counter
import pymorphy3

morph = pymorphy3.MorphAnalyzer()

STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все", "она", "так",
    "его", "но", "да", "ты", "к", "у", "же", "вы", "за", "бы", "по", "только", "ее", "мне", "было",
    "вот", "от", "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг",
    "ли", "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж",
    "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть", "надо",
    "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз",
    "тоже", "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой",
    "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас", "были",
    "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два", "об", "другой", "хоть", "после",
    "над", "больше", "тот", "через", "эти", "нас", "про", "всего", "них", "какая", "много", "разве",
    "три", "эту", "моя", "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть", "том",
    "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между"
}
POS_EXCLUDE = {"PREP", "CONJ", "PRCL", "INTJ", "NPRO"}
POSITIVE_WORDS = {"хороший", "отличный", "супер", "крутой", "любить", "нравиться", "радость", "класс", "прекрасный", "успех", "лучший", "полезный", "добрый"}
NEGATIVE_WORDS = {"плохой", "ужасный", "ненавидеть", "бесить", "отстой", "кошмар", "злой", "провал", "тупой", "мерзкий", "отвратительный", "печальный"}
TOXIC_WORDS = {"идиот", "тупой", "дурак", "дебил", "ненавижу", "мразь", "урод", "сволочь"}


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r"[A-Za-zА-Яа-яЁё0-9\-]+", text.lower())


def normalize_word(word: str) -> tuple[str, str | None]:
    parsed = morph.parse(word)[0]
    return parsed.normal_form, parsed.tag.POS


def analyze_text(text: str) -> dict:
    tokens = tokenize(text)
    if not tokens:
        return {
            "n_words": 0,
            "n_inform_word": 0,
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "toxicity_score": 0.0,
            "topics": json.dumps([], ensure_ascii=False),
            "top": None,
        }

    informative = []
    for token in tokens:
        lemma, pos = normalize_word(token)
        if lemma not in STOPWORDS and pos not in POS_EXCLUDE and len(lemma) > 2:
            informative.append(lemma)

    counts = Counter(informative)
    topics = [word for word, _ in counts.most_common(5)]
    top_word = counts.most_common(1)[0][0] if counts else None

    pos_cnt = sum(1 for word in informative if word in POSITIVE_WORDS)
    neg_cnt = sum(1 for word in informative if word in NEGATIVE_WORDS)
    toxic_cnt = sum(1 for word in informative if word in TOXIC_WORDS)

    sent_score = (pos_cnt - neg_cnt) / max(len(informative), 1)
    if sent_score > 0.03:
        sentiment = "positive"
    elif sent_score < -0.03:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "n_words": len(tokens),
        "n_inform_word": len(informative),
        "sentiment": sentiment,
        "sentiment_score": round(sent_score, 4),
        "toxicity_score": round(toxic_cnt / max(len(informative), 1), 4),
        "topics": json.dumps(topics, ensure_ascii=False),
        "top": top_word,
    }
