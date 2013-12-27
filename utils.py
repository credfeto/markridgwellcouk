import os
import re
import unicodedata
import hashlib

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

def site_url(path):
    return 'https://markridgwell-data.s3.amazonaws.com' + path

def image_url( path, image ):

    base = path[7:]
    filestub = base[base.rfind('/', 0, len(base) -2 )+1:-1]

    return site_url( base + filestub + '-' + str(image.width) +'x' +str(image.height) + '.jpg')

def is_development():
    appId = os.environ['APPENGINE_RUNTIME']

    return appId == 'dev~markridgwellcouk'

def generate_url_hash(searchPath):
    return hashlib.sha512(searchPath).hexdigest()

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
