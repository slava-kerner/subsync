from guess_language import guess_language


def detect_language(text):
    lng = guess_language(text)
    if lng == 'UNKNOWN':
        lng = None
    return lng


def detect_subtitle_language(subtitle):
    """
    :param subtitle: Subtitle 
    :return: e.g. 'en', or None if failed 
    """
    full_text = '. '.join(item.text_without_tags for item in subtitle)
    return detect_language(full_text)
