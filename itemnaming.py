import utils


def get_album_title(publish):

    if publish.breadcrumbs is not None:
        album = publish.breadcrumbs[-1]
        if album is not None:
            album_title = album.title
            pos = album_title.find('-')
            if pos != -1:
                album_title = album_title[pos + 1:]
            album_title = album_title.strip()

            return album_title

    return None


def photo_title(publish, title_max_length):
    album_title = get_album_title(publish)
    title = utils.strip_trailing_numbers(publish.title)
    if album_title is not None:
        if not utils.contains_either(title.lower().strip(), album_title.lower().strip()):
            title = title + " - " + album_title
            if len(title) > title_max_length:
                title = title[:title_max_length]
    return title
