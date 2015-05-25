import utils


def get_album_title(publish):

    if publish.breadcrumbs is not None:
        total_crumbs = len(publish.breadcrumbs)
        if total_crumbs > 1:
            album = publish.breadcrumbs[-1]
            if album is not None:
                album_title = album.title
                pos = album_title.find('-')
                if pos != -1:
                    album_title = album_title[pos + 1:]
                album_title = album_title.strip()

                return album_title

    return None


def contains_album(photo, album):
    if utils.contains_either(photo, album):
        return True

    album_parts = album.split('-')
    for part in album_parts:
        if part.strip() in photo:
            return True

    return False

def contains_keyword(keyword, search_photo_title, search_album_title):
    return utils.contains_either(keyword, search_photo_title) or utils.contains_either(keyword, search_album_title)

def publish_hashtags(publish):

    hash_tags = ['#photo']

    title = publish.title.lower().strip()
    album_title = get_album_title(publish).lower().strip()

    if contains_keyword('harlow', title, album_title):
        hash_tags.append('#ProudOfHarlow')

    if contains_keyword('onefloyd', title, album_title):
        hash_tags.append('#OneFloyd')

    if contains_keyword('one floyd', title, album_title):
        hash_tags.append('#OneFloyd')

    if contains_keyword('heart4harlow', title, album_title):
        hash_tags.append('#ProudOfHarlow')
        hash_tags.append('#Heart4Harlow')

    if contains_keyword('rock school', title, album_title):
        hash_tags.append('#ProudOfHarlow')
        hash_tags.append('#RockSchoolHarlow')

    return hash_tags

def photo_title(publish, title_max_length):
    album_title = get_album_title(publish)
    title = utils.strip_trailing_numbers(publish.title)
    if album_title is not None:

        if not contains_album(title.lower().strip(), album_title.lower().strip()):
            title = title + " - " + album_title
            if len(title) > title_max_length:
                title = title[:title_max_length]
    return title
