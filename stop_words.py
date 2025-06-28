import re

MESSAGE_REMOVE_PATTERN = re.compile(
    r"(?i)"
    r"pump\.?fun|"
    r"\w{40}pump|"
    r"to\sjoin\sprivate\ssignal|"
    r"first\s10\speople\sto\sdm\si\swill|"
    r"who\sneed\s(sol|the\ssol)|"
    r"next\srunner\s\w{40}|"
    r"hello\sadmin\sand\scommunity|"
    r"some\sof\smy\sservices\sinclude|"
    r"promotion\son\smy\stelegram|"
    r"you\sneed\sgood\spromotion|"
    r"i\shave\strusted\sreal\sinvestor|"
    r"if\syou\sneed\spromotion\,\sdm\sme|"
    r"mass\sdm|"
    r"dm\snow|"
    r"crypto\spromo\sloaded|"
    r"launch(ing)?\ssoon.?.?.?.?.?sol|"
    r"shill\sme\syour\sx100\sgem|"
    r"wif.?hat|"
    r"from\s(the\s)?(team|dev|same\sdevs?)\swho|"
    r"still\sthe\samerica.?party|"
    r"wif.?h|"
    r"t.me..\w{16}|"
    r"i\swant\sto\sgive\s.{0,7}\ssol|"
    r"check\smy\sbio|"
    r"in\smy\sprivate|"
    r"my\sportfolio\schannel|"
    r"(?=.*\bdesign\b)(?=.*\bdm\b)(?=.*\blogo\b)(?=.*\bstic?ker\b)|"
    r"shill\sme|"
    r"buy\sused\ssolana\swallet|"
    r"let.?s\sgo\smy\sbii?o|"
    r"in\smy\sbii?o"

)

# 44-символьный ID-паттерн
ID_PATTERN = re.compile(r"\b([A-Za-z0-9]{44})\b")

# Разрешённые ID (например, токен проекта)
ALLOWED_IDS = {
    "DfYVDWY1ELNpQ4s1CK5d7EJcgCGYw27DgQo2bFzMH6fA",
    "HU9TSBH3HsY1GFAtCNsAX2B5jCvt7D8WFR29ioL54rgn",
    "E8iZHoRdr6uJEB1VtF6JJbRz286KAh3hw8BByUQcRFTs"
}

def contains_blocked_id(text: str) -> bool:
    """Проверка на 44-символьный ID, не входящий в белый список"""
    matches = ID_PATTERN.findall(text)
    for match in matches:
        if match not in ALLOWED_IDS:
            return True
    return False

def is_spam_message(text: str) -> bool:
    """Возвращает True, если сообщение считается спамом"""
    return MESSAGE_REMOVE_PATTERN.search(text) or contains_blocked_id(text)