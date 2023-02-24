from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def keywords_threshold(keyword_score):
    if keyword_score > 0.95:
        return "is-success"
    elif 0.7 < keyword_score <= 0.95:
        return "is-warning"
    elif 0 < keyword_score <= 0.7:
        return "is-danger"
    else:
        return ""


@register.filter
def first_n_char(text, n_characters):
    return text[:n_characters]


@register.filter
def first_n_words(text, n_words):
    return " ".join(text.split()[:n_words])


@register.filter
def first_n_items(list_of_items, n_items):
    return list_of_items[:n_items]


@register.filter
def last_n_items(list_of_items, n_items):
    return list_of_items[-n_items:]


@register.filter
def convert_papers_list(papers, data_format_version):
    """data_format_version 1 and 2 are lists, 3 is a dict"""
    if data_format_version < 3:
        return papers
    else:
        return papers.values()


@register.filter
def is_field_required(review:dict, field:str) -> str:
    """returns True if the field is required"""
    if field in review.obligatory_fields:
        return 'required'
    else:
        return ''

@register.filter
def _hash(h, key):
    return h[key]
