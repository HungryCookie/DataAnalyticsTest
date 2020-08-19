import re
import unicodedata


def normalize_text(text):
    """
    Normalizes string to the standard similar format (without numbers, special symbols, etc..)
    :param text: string
    :return: formatted string
    """
    text = re.sub("\d+", "", text)  # number removing
    text = re.sub(" {2,}", " ", text).lower()  # space removing
    text = re.sub("[^\w\s]", "", text)  # special symbols removing
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')  # symbol replacement
    return text.decode("utf-8")