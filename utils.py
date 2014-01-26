import os
import re
import unicodedata
import hashlib

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import sys

def should_track( headers ):

    track = headers.get('DNT', "0")

    if track is None:
        return True

    if track == "1":
        return False

    return True

def site_url(path):
    return 'https://markridgwell-data.s3.amazonaws.com' + path

def pathify_hash( hash ):
    indexes = [ 2, 4, 8, 12, 20 ];
    indexes.sort(reverse = True)

    base = hash;
    for idx in indexes:
        base = base[:idx] + '/' + base[idx:]

    return base

def image_url( path, image ):

    hash = generate_image_url_hash(path);
    base = pathify_hash( hash )
        
    filestub = path[path.rfind('/', 0, len(path)-2)+1:-1]

    return site_url( '/' + base + '/' + filestub + '-' + str(image.width) +'x' +str(image.height) + '.jpg')

def convert_old_url( originalPath ):

    base = originalPath
    
    tildePos = base.rfind('/~')
    if tildePos <> -1:
        base = base[:tildePos+1]
    else:
        tildePos = base.rfind('/%7e')
        if tildePos <> -1:
            base = base[:tildePos+1]

    root =  base.strip();
    
    replacedWrongSlash = root.replace("\\", "/" )
    replacedDuplicateHyphens = re.sub(r"[^a-z0-9\-/]", "-", replacedWrongSlash)
    replacedBadChars = re.sub(r"(\-{2,})", "-", replacedDuplicateHyphens )
    replacedEndingHyphens = replacedBadChars.rstrip('-') 

    if replacedEndingHyphens.endswith( '/' ) == False:
        replacedEndingHyphens = replacedEndingHyphens + '/'

    return replacedEndingHyphens

def is_development():
    appId = os.environ['APPENGINE_RUNTIME']

    return appId == 'dev~markridgwellcouk'

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
