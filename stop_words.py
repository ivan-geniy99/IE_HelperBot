import re

MESSAGE_REMOVE_PATTERN = re.compile(
    r"(?i)"
    r"pump\.fun|"
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
    r"launching\ssoon|"
    r"shill\sme\syour\sx100\sgem"
)
