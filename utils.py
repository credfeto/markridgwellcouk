import os
import re
import unicodedata
import hashlib
import models

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import sys

import googl
import logging

def is_cron_task(headers):
    hdr = headers.get('X-AppEngine-Cron', 'false')

    if hdr is None:
        return False

    if hdr == "true":
        return True

    return False


def is_public_publishable_path(path):
    return path.startswith('/albums/') and not path.startswith('/albums/private/')


def enable_windows_share_metadata(userAgent):
    if userAgent is None:
        return True

    agent = userAgent.lower()

    if 'facebookexternalhit' in agent:
        return False

    if 'twitter' in agent:
        return False

    if 'google (+' in agent:
        return False

    if 'appdotnet' in agent:
        return False

    if 'google-http-java-client' in agent:
        return False

    return True

def should_track(headers):
    track = headers.get('DNT', "0")

    if track is None:
        user_agent = headers.get('User-Agent', None)
        if user_agent is not None:
            return not should_share(user_agent)
        return True

    if track == "1":
        return False

    return True


def should_share(userAgent):
    if userAgent is None:
        return True

    agent = userAgent.lower()

    if 'googlebot' in agent:
        return False

    if 'googlebot-news' in agent:
        return False

    if 'googlebot-image' in agent:
        return False

    if 'googlebot-video' in agent:
        return False

    if 'googlebot-mobile' in agent:
        return False

    if 'mediapartners-google' in agent:
        return False

    if 'mediapartners (googlebot)' in agent:
        return False

    if 'adsbot-google' in agent:
        return False

    if 'msnbot' in agent:
        return False

    if 'bingbot' in agent:
        return False

    if 'slurp' in agent:
        return False

    if 'facebookexternalhit' in agent:
        return False

    if 'appdotnet' in agent:
        return False

    if 'baiduspider' in agent:
        return False

    if 'yandexbot' in agent:
        return False

    if 'teoma' in agent:
        return False

    if 'exabot' in agent:
        return False

    if 'tweetmemebot' in agent:
        return False

    if 'bingpreview' in agent:
        return False

    if 'tweetedtimes' in agent:
        return False

    if 'mj12bot' in agent:
        return False

    if 'showyoubot' in agent:
        return False

    if 'bufferbot' in agent:
        return False

    if 'google-http-java-client' in agent:
        return False

    if 'mail.ru_bot' in agent:
        return False

    if 'feedfetcher-google' in agent:
        return False

    return True


def site_url(path):
    return 'https://markridgwell-data.s3.amazonaws.com' + path


def redirect_url(path, query_string):
    if is_development() == False:
        path = 'https://www.markridgwell.co.uk' + path
    if path.endswith('/') == False:
        path = path + '/'
    if query_string and len(query_string) > 0:
        path = path + '?' + query_string

    return path


def pathify_hash(hash):
    indexes = [2, 4, 8, 12, 20]
    indexes.sort(reverse=True)

    base = hash;
    for idx in indexes:
        base = base[:idx] + '/' + base[idx:]

    return base


def image_url(path, image):
    hash = generate_image_url_hash(path)
    base = pathify_hash(hash)

    filestub = path[path.rfind('/', 0, len(path) - 2) + 1:-1]

    return site_url('/' + base + '/' + filestub + '-' + str(image.width) + 'x' + str(image.height) + '.jpg')


def make_url(root):
    replacedWrongSlash = root.replace("\\", "/")
    replacedDuplicateHyphens = re.sub(r"[^a-z0-9\-/]", "-", replacedWrongSlash)
    replacedBadChars = re.sub(r"(\-{2,})", "-", replacedDuplicateHyphens)
    replacedHyphensNextToSlash = re.sub(r"(\-*/\-*)", "/", replacedBadChars)
    replacedEndingHyphens = replacedHyphensNextToSlash.rstrip('-')
    if replacedEndingHyphens.endswith('/') == False:
        replacedEndingHyphens = replacedEndingHyphens + '/'
    return replacedEndingHyphens


def convert_old_url(originalPath):
    base = originalPath

    tildePos = base.rfind('/~')
    if tildePos <> -1:
        base = base[:tildePos + 1]
    else:
        tildePos = base.rfind('/%7e')
        if tildePos <> -1:
            base = base[:tildePos + 1]

    root = base.strip()

    # remove image paths and convert them to a normal url
    if root.startswith('/image/'):
        lastSlashPos = root.rfind('/')
        root = root[6:lastSlashPos]

    return make_url(root)


def is_development():
    env = os.environ['SERVER_SOFTWARE']

    return env.startswith('Development/')


def device_supports_ssl_tni(userAgent):
    # agent = userAgent.lower()
    #
    # if 'chrome' in agent:
    #     return True
    #
    # if 'firefox' in agent:
    #     return True
    #
    # if 'opera' in agent:
    #     return True
    #
    # if 'googlebot' in agent:
    #     return True
    #
    # if 'msnbot' in agent:
    #     return True
    #
    # if 'bingbot' in agent:
    #     return True
    #
    # return False
    return True

def generate_host_hash(host):
    return re.sub('[^a-zA-Z0-9-]+', '-', host).strip('-')


def generate_url_hash(searchPath):
    return hashlib.sha512(searchPath).hexdigest()


def generate_image_url_hash(searchPath):
    return hashlib.sha512(searchPath[8:]).hexdigest()


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    return re.sub('[^a-zA-Z0-9-]+', '-', s).strip('-')


def render_template(template_name, template_vals=None):
    if not template_vals:
        template_vals = {}
    template_vals.update({
        'template_name': template_name,
        'devel': os.environ['SERVER_SOFTWARE'].startswith('Devel'),
    })
    template_path = os.path.join("views", template_name)
    return template.render(template_path, template_vals)


def find_double_size(orderedResizes, width):
    doubleWidth = width * 2
    for (i, resize ) in enumerate(orderedResizes):
        if resize.width == doubleWidth:
            return resize

    return None


def build_image_css(item, orderedResizes):
    first = None
    last = None
    newLine = ''  # '\n'
    imageMargin = 150
    resizecss = ''

    base_image_path = item.path
    if item.originalAlbumPath:
        base_image_path = item.originalAlbumPath

    for (i, resize ) in enumerate(orderedResizes):
        if first is None:
            first = resize  # Set the default image size
            resizecss = resizecss + newLine
            resizecss = resizecss + '.image{' + newLine
            resizecss = resizecss + 'width:' + str(resize.width) + 'px;' + newLine
            resizecss = resizecss + 'height:' + str(resize.height) + 'px;' + newLine
            resizecss = resizecss + 'min-width:' + str(resize.width) + 'px;' + newLine
            resizecss = resizecss + 'min-height:' + str(resize.height) + 'px;' + newLine
            resizecss = resizecss + 'max-width:' + str(resize.width) + 'px;' + newLine
            resizecss = resizecss + 'max-height:' + str(resize.height) + 'px;' + newLine
            resizecss = resizecss + 'background-color:transparent;' + newLine
            resizecss = resizecss + 'background-repeat:no-repeat;' + newLine
            resizecss = resizecss + 'background-position:top left;' + newLine
            resizecss = resizecss + 'background-image:url(\'' + image_url(base_image_path, resize) + '\');' + newLine

            doubleSize = find_double_size(orderedResizes, resize.width);
            if doubleSize <> None:
                resizecss = resizecss + '@media only screen and (-Webkit-min-device-pixel-ratio: 1.5),'
                resizecss = resizecss + 'only screen and (-moz-min-device-pixel-ratio: 1.5),'
                resizecss = resizecss + 'only screen and (-o-min-device-pixel-ratio: 3/2),'
                resizecss = resizecss + 'only screen and (min-device-pixel-ratio: 1.5) {' + newLine
                resizecss = resizecss + 'background-image:url(\'' + image_url(base_image_path, doubleSize) + '\');' + newLine
                resizecss = resizecss + 'background-size:' + str(doubleSize.width / 2) + 'px ' + str(
                    doubleSize.height / 2) + 'px;' + newLine
                resizecss = resizecss + '}' + newLine

            resizecss = resizecss + '}' + newLine
            resizecss = resizecss + newLine

        last = resize
        resizecss = resizecss + newLine
        if i < (len(item.resizes) - 1):
            resizecss = resizecss + '@media (min-width:' + str(
                resize.width + imageMargin) + 'px) and (max-width:' + str(
                orderedResizes[i + 1].width + imageMargin - 1) + 'px){' + newLine
        else:
            resizecss = resizecss + '@media(min-width:' + str(resize.width + imageMargin) + 'px) {' + newLine
        resizecss = resizecss + '.image {' + newLine
        resizecss = resizecss + 'width:' + str(resize.width) + 'px;' + newLine
        resizecss = resizecss + 'height:' + str(resize.height) + 'px;' + newLine
        resizecss = resizecss + 'min-width:' + str(resize.width) + 'px;' + newLine
        resizecss = resizecss + 'min-height:' + str(resize.height) + 'px;' + newLine
        resizecss = resizecss + 'tmax-width:' + str(resize.width) + 'px;' + newLine
        resizecss = resizecss + 'tmax-height:' + str(resize.height) + 'px;' + newLine
        resizecss = resizecss + 'background-image:url(\'' + image_url(base_image_path, resize) + '\');' + newLine

        doubleSize = find_double_size(orderedResizes, resize.width);
        if doubleSize <> None:
            resizecss = resizecss + '@media only screen and (-Webkit-min-device-pixel-ratio: 1.5),'
            resizecss = resizecss + 'only screen and (-moz-min-device-pixel-ratio: 1.5),'
            resizecss = resizecss + 'only screen and (-o-min-device-pixel-ratio: 3/2),'
            resizecss = resizecss + 'only screen and (min-device-pixel-ratio: 1.5){' + newLine
            resizecss = resizecss + 'background-image:url(\'' + image_url(base_image_path, doubleSize) + '\');' + newLine
            resizecss = resizecss + 'background-size:' + str(doubleSize.width / 2) + 'px ' + str(
                doubleSize.height / 2) + 'px;' + newLine
            resizecss = resizecss + '}' + newLine

        resizecss = resizecss + '}'
        resizecss = resizecss + '}' + newLine
        resizecss = resizecss + newLine

    if len(resizecss) == 0:
        return None
    return {'css': resizecss, 'first': first, 'last': last}


def path_to_tagId(path):
    filestub = path[path.rfind('/', 0, len(path) - 2) + 1:-1]

    return filestub


def add_response_headers(request, headers):
    headers['Vary'] = 'DNT'
    headers['P3P'] = 'max-age=31536000'
    headers['Access-Control-Allow-Origin'] = "'self'"
    headers['Access-Control-Allow-Methods'] = "GET, HEAD, OPTIONS"
    headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    headers['X-Frame-Options'] = "SAMEORIGIN"

    userAgent = request.headers.get('User-Agent', None)

    if not is_development() and request.scheme == 'https' and device_supports_ssl_tni(userAgent):
        headers['Strict-Transport-Security'] = 'max-age=31536000'


def shortern_url(url):
    # try:
    api = googl.Googl("AIzaSyAR7DxhhrftPkmbUNrj5rHMl4qaKKkR5JQ")

    shortened = api.shorten(url)

    return shortened["id"]

    #except googl.GooglError:
    #    return url


def contains_either(photo_title, album_title):
    if album_title in photo_title:
        return True

    if photo_title in album_title:
        return True

    return False


def strip_trailing_numbers(item):
    return item.rstrip('0123456789 ')


def is_publishable(item):

    if item.keywords:
        for keyword in item.keywords:
            if keyword.lower() == 'nsfw':
                return False

    return True


def generate_keyword_url(host, keyword, item_to_select):

    replacedWrongSlash = keyword.lower().replace("\\", "/")
    replacedDuplicateHyphens = re.sub(r"[^a-z0-9\-/]", "-", replacedWrongSlash)
    replacedBadChars = re.sub(r"(\-{2,})", "-", replacedDuplicateHyphens)
    replacedHyphensNextToSlash = re.sub(r"(\-*/\-*)", "/", replacedBadChars)
    replacedEndingHyphens = replacedHyphensNextToSlash.rstrip('-')
    replacedEndingHyphens = replacedEndingHyphens.lstrip('-')
    if replacedEndingHyphens.endswith('/') == False:
        replacedEndingHyphens = replacedEndingHyphens + '/'

    urlsafe_keyword = replacedEndingHyphens

    url =   host + "/keywords/" + urlsafe_keyword[0:1] + "/" + urlsafe_keyword

    if item_to_select:
        return url + '#' + item_to_select
    else:
        return url
