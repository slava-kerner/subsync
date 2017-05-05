from guess_language import guess_language
import langid


class LanguageDetector:
    all_methods = ['guess_language', 'langid']

    def __init__(self, method=None, **kwargs):
        self.methods = [method] if method else self.all_methods
        self.config = kwargs

    def _detect(self, text, method):
        if method == 'guess_language':
            lng = guess_language(text)
            if lng == 'UNKNOWN':
                lng = None
            prob = 1
        elif method == 'langid':
            lng, prob = langid.classify(text)
        else:
            raise Exception('method %s not supported' % method)
        return lng, prob

    def detect(self, text):
        results = [self._detect(text, method) for method in self.methods]
        languages = [result[0] for result in results]
        most_common_lang = max(set(languages) - {None}, key=languages.count)
        return most_common_lang  # todo bayesian


def detect_subtitle_language(subtitle, **kwargs):
    """
    :param subtitle: Subtitle 
    :return: e.g. 'en', or None if failed 
    """
    full_text = '. '.join(item.text_without_tags for item in subtitle)
    detector = LanguageDetector(kwargs)
    return detector.detect(full_text)
