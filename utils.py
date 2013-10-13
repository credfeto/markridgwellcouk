import os
import re
import unicodedata

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


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
