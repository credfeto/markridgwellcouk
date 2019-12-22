import os
import re
import unicodedata
import hashlib
import models
import datetime

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

def generate_host_hash(host):
    return re.sub('[^a-zA-Z0-9-]+', '-', host).strip('-')


def decode_unicode_chars(text):
    try:
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    except:
        return text

def generate_random_id():

    now = datetime.datetime.now()

    formatted = "IDHash:" + now.isoformat('T')

    return hashlib.sha512(formatted).hexdigest()

def generate_url_hash(search_path):

    decoded = decode_unicode_chars(search_path)

    return hashlib.sha512(decoded).hexdigest()


def generate_image_url_hash(search_path):

    decoded = decode_unicode_chars(search_path)

    return hashlib.sha512(decoded[8:]).hexdigest()


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


def find_double_size(ordered_resizes, width):
    double_width = width * 2
    for (i, resize ) in enumerate(ordered_resizes):
        if resize.width == double_width:
            return resize

    return None


def build_image_css(item, ordered_resizes):
    first = None
    last = None
    new_line = ''  # '\n'
    image_margin = 150
    resize_css = ''

    base_image_path = item.path
    if item.originalAlbumPath:
        base_image_path = item.originalAlbumPath

    for (i, resize) in enumerate(ordered_resizes):
        if first is None:
            first = resize  # Set the default image size
            resize_css = resize_css + new_line
            resize_css = resize_css + '.image{' + new_line
            resize_css = resize_css + 'width:' + str(resize.width) + 'px;' + new_line
            resize_css = resize_css + 'height:' + str(resize.height) + 'px;' + new_line
            resize_css = resize_css + 'min-width:' + str(resize.width) + 'px;' + new_line
            resize_css = resize_css + 'min-height:' + str(resize.height) + 'px;' + new_line
            resize_css = resize_css + 'max-width:' + str(resize.width) + 'px;' + new_line
            resize_css = resize_css + 'max-height:' + str(resize.height) + 'px;' + new_line
            resize_css = resize_css + 'background-color:transparent;' + new_line
            resize_css = resize_css + 'background-repeat:no-repeat;' + new_line
            resize_css = resize_css + 'background-position:top left;' + new_line
            resize_css = resize_css + 'background-image:url(\'' + image_url(base_image_path, resize) + '\');' + new_line

            double_size = find_double_size(ordered_resizes, resize.width);
            if double_size <> None:
                resize_css = resize_css + '@media only screen and (-Webkit-min-device-pixel-ratio: 1.5),'
                resize_css = resize_css + 'only screen and (-moz-min-device-pixel-ratio: 1.5),'
                resize_css = resize_css + 'only screen and (-o-min-device-pixel-ratio: 3/2),'
                resize_css = resize_css + 'only screen and (min-device-pixel-ratio: 1.5) {' + new_line
                resize_css = resize_css + 'background-image:url(\'' + image_url(base_image_path, double_size) + '\');' + new_line
                resize_css = resize_css + 'background-size:' + str(double_size.width / 2) + 'px ' + str(
                    double_size.height / 2) + 'px;' + new_line
                resize_css = resize_css + '}' + new_line

            resize_css = resize_css + '}' + new_line
            resize_css = resize_css + new_line

        last = resize
        resize_css = resize_css + new_line
        if i < (len(item.resizes) - 1):
            resize_css = resize_css + '@media (min-width:' + str(
                resize.width + image_margin) + 'px) and (max-width:' + str(
                ordered_resizes[i + 1].width + image_margin - 1) + 'px){' + new_line
        else:
            resize_css = resize_css + '@media(min-width:' + str(resize.width + image_margin) + 'px) {' + new_line
        resize_css = resize_css + '.image {' + new_line
        resize_css = resize_css + 'width:' + str(resize.width) + 'px;' + new_line
        resize_css = resize_css + 'height:' + str(resize.height) + 'px;' + new_line
        resize_css = resize_css + 'min-width:' + str(resize.width) + 'px;' + new_line
        resize_css = resize_css + 'min-height:' + str(resize.height) + 'px;' + new_line
        resize_css = resize_css + 'tmax-width:' + str(resize.width) + 'px;' + new_line
        resize_css = resize_css + 'tmax-height:' + str(resize.height) + 'px;' + new_line
        resize_css = resize_css + 'background-image:url(\'' + image_url(base_image_path, resize) + '\');' + new_line

        double_size = find_double_size(ordered_resizes, resize.width);
        if double_size <> None:
            resize_css = resize_css + '@media only screen and (-Webkit-min-device-pixel-ratio: 1.5),'
            resize_css = resize_css + 'only screen and (-moz-min-device-pixel-ratio: 1.5),'
            resize_css = resize_css + 'only screen and (-o-min-device-pixel-ratio: 3/2),'
            resize_css = resize_css + 'only screen and (min-device-pixel-ratio: 1.5){' + new_line
            resize_css = resize_css + 'background-image:url(\'' + image_url(base_image_path, double_size) + '\');' + new_line
            resize_css = resize_css + 'background-size:' + str(double_size.width / 2) + 'px ' + str(
                double_size.height / 2) + 'px;' + new_line
            resize_css = resize_css + '}' + new_line

        resize_css = resize_css + '}'
        resize_css = resize_css + '}' + new_line
        resize_css = resize_css + new_line

    if len(resize_css) == 0:
        return None
    return {'css': resize_css, 'first': first, 'last': last}


def path_to_tagId(path):
    filestub = path[path.rfind('/', 0, len(path) - 2) + 1:-1]

    return filestub


def add_response_headers(request, headers):
    headers['Vary'] = 'DNT'
    headers['P3P'] = 'max-age=31536000'
    headers['Access-Control-Allow-Origin'] = "'self'"
    headers['Access-Control-Allow-Methods'] = "GET, HEAD, OPTIONS"
    headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    headers['X-Frame-Options'] = "DENY"
    headers['X-XSS-Protection'] = "1; mode=block"
    headers['X-Content-Type-Options'] = "nosniff"
    headers['Referrer-Policy'] = "no-referrer"

    user_agent = request.headers.get('User-Agent', None)

    if not is_development() and request.scheme == 'https':
        headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubdomains; preload'

def shortern_url(url):
    return url

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

    replaced_wrong_slash = keyword.lower().replace("\\", "/")
    replaced_duplicate_hyphens = re.sub(r"[^a-z0-9\-/]", "-", replaced_wrong_slash)
    replaced_bad_chars = re.sub(r"(\-{2,})", "-", replaced_duplicate_hyphens)
    replaced_hyphens_next_to_slash = re.sub(r"(\-*/\-*)", "/", replaced_bad_chars)
    replaced_ending_hyphens = replaced_hyphens_next_to_slash.rstrip('-')
    replaced_ending_hyphens = replaced_ending_hyphens.lstrip('-')
    if replaced_ending_hyphens.endswith('/') == False:
        replaced_ending_hyphens = replaced_ending_hyphens + '/'

    urlsafe_keyword = replaced_ending_hyphens

    url = host + "/keywords/" + urlsafe_keyword[0:1] + "/" + urlsafe_keyword

    if item_to_select:
        return url + '#' + item_to_select
    else:
        return url
