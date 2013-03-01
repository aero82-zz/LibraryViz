#!/usr/bin/env python

import datetime
import logging
import os
import webapp2
import json

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import urlfetch

  
class Book(db.Model):
  """Books"""
  
  title = db.StringProperty(required=True)
  author = db.StringProperty(required=True)
  pages = db.IntegerProperty(required=True)
  type = db.StringProperty(required=True)
  genre = db.StringProperty(required=True)
  url = db.LinkProperty()
  created = db.DateTimeProperty(auto_now_add=True)
  sheet_key = db.StringProperty(required=True)

      
class BaseRequestHandler(webapp.RequestHandler):
  """Supplies a common template generation functions.  Extends the input
     values with common variables and template paths."""
  
  def generate(self, template_name, template_values={}):
    values = {
      'request': self.request,
      'application_name': 'Book Gallery',
    }
    values.update(template_values)
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', template_name))
    self.response.out.write(template.render(path, values, debug=True))
    
class BookPageHandler(BaseRequestHandler):

  def get(self):
    key = self.request.get('key')
    #key = '0AuNMfuFP51vedEg1dk9uVERqREZ4dl9Rd185LXN2Z0E'
    books = db.Query(Book).filter('sheet_key =', key)

    self.generate('library.html', {'books': books})
    
class LoadBooksHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write('Loading')
    key = self.request.get('key')
    if key:
      url = 'http://spreadsheets.google.com/feeds/list/' + key + '/od6/public/values?alt=json'
      result = urlfetch.fetch(url)
      if result.status_code == 200:
        feed_obj = json.loads(result.content)
        if "feed" in feed_obj:
          entries = feed_obj['feed']['entry']
          books = []
          for entry in entries:
            book = {}
            book['author'] = entry['gsx$authordetails']['$t']
            book['title'] = entry['gsx$title']['$t']
            book['pages'] = entry['gsx$pages']['$t']
            book['type'] = entry['gsx$type']['$t']
            book['genre'] = entry['gsx$genre']['$t']            
            check_books = db.Query(Book).filter('sheet_key =', key).filter('title = ', book['title'])
            
            if not check_books.count():
              books.append(book)
              book['rpc'] = setupRPC(book['author'],book['title'])
            else:
              logging.info(book['title'] + ' already in datastore for this key')
            #url = fetchImageUrl(author, title)
            #url = db.Link(entry['gsx$url']['$t'].replace('curl','normal'))
          
          for book in books:
            url = fetchURL(book['rpc'])
            new_book = Book(author=book['author'], title=book['title'], pages=int(book['pages']), type=book['type'], genre=book['genre'], url=url, sheet_key=key)
            logging.info('Added ' + book['title'] + ' by ' + book['author'])
            new_book.put()
    
      self.response.out.write('<br><a href="/book?key=' + key +'">Ready</a>')
    else:
      self.response.out.write('Need to provide a key')

def setupRPC(author, title):
  key = 'AIzaSyCKhnVBlbRD_JJlEHMm04Sy3-ti7jr-JAk'
  query = 'inauthor:' + author.split(',')[0] + '+' + 'intitle:' + title.replace(' ','+')
  url = 'https://www.googleapis.com/books/v1/volumes?q=' + query + '&key=' + key
  rpc = urlfetch.create_rpc()
  urlfetch.make_fetch_call(rpc, url)
  
  return rpc

def fetchURL(rpc):
  result = rpc.get_result()
  if (result.status_code == 200):
    json_book = json.loads(result.content)
    for entry in json_book['items']:
      book = entry['volumeInfo']
      if ('imageLinks' in book.keys()):
        return db.Link(book['imageLinks']['thumbnail'])
      else:
        return 'http://www.google.com'
  else:
    logging.info(result.status_code)
    
app = webapp2.WSGIApplication([('/', BookPageHandler),('/load', LoadBooksHandler)])

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    webapp.util.run_wsgi_app(app)

if __name__ == '__main__':
  main()