from bs4 import BeautifulSoup, Comment
import urllib.parse

def innerHTML(element):
  return element.decode_contents(formatter="html")

def prettify_body(markup):
  """
  dump the body
  """
  soup = BeautifulSoup(markup, 'html.parser')
  return soup.body.prettify()

def clean(markup):
  """ 
  apply whitelisting functions
  """
  html = safe_html(markup)
  soup = BeautifulSoup(html, 'html.parser')
  return soup.prettify()

def ungoogle_link(url):
  """
  take a URL like https://www.google.com/url?q=[URL]
  and return the [URL] part
  """
  if "www.google.com/url" in url:
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    if 'q' in qs:
      return urllib.parse.unquote(qs['q'][0])
  return url


# the below is from http://chase-seibert.github.io/blog/2011/01/28/sanitize-html-with-beautiful-soup.html
def safe_html(html):
  if not html:
    return None

  # remove these tags, complete with contents.
  blacklist = ["script", "style"]

  whitelist = [
    "p", "br", "pre",
    "table", "tbody", "thead", "tr", "td", "th",
    "a",
    "blockquote", "cite",
    "ul", "li", "ol",
    "b", "em", "i", "strong", "u",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "img", "span"
    ]

  try:
    # BeautifulSoup is catching out-of-order and unclosed tags, so markup
    # can't leak out of comments and break the rest of the page.
    soup = BeautifulSoup(html, 'html.parser')
  except HTMLParseError as e:
    # special handling?
    raise e

  # now strip HTML we don't like.
  for tag in soup.findAll():
    if tag.name.lower() in blacklist:
      # blacklisted tags are removed in their entirety
      tag.extract()
    elif tag.name.lower() in whitelist:
      # tag is allowed. Make sure all the attributes are allowed.
      tag.attrs = {k: safe_css(k, tag.attrs[k]) for k in tag.attrs if _attr_name_whitelisted(k)}
    else:
      # not a whitelisted tag. I'd like to remove it from the tree
      # and replace it with its children. But that's hard. It's much
      # easier to just replace it with an empty span tag.
      tag.name = "span"
      tag.attrs = []

  # scripts can be executed from comments in some cases
  comments = soup.findAll(text=lambda text:isinstance(text, Comment))
  for comment in comments:
    comment.extract()

  # clean out the spans
  for tag in soup.findAll('span'):
    tag.unwrap()

  # un-google the links
  for tag in soup.findAll('a'):
    if 'href' in tag.attrs:
      tag.attrs['href'] = ungoogle_link(tag.attrs['href'])

  safe_html = str(soup)

  if safe_html == ", -":
    return None

  return safe_html

def _attr_name_whitelisted(attr_name):
    return attr_name.lower() in ["href", "title", "alt", "src"]

def safe_css(attr, css):
  if attr == "style":
    return re.sub("(width|height):[^;]+;", "", css)
  return css