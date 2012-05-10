

from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode

import logging, time, base64

from urlparse import urlunparse

from elementtree import ElementTree


def http_get(url, username='', password=''):
  "Do an HTTP Get with optional Basic authorization"
  request = Request(url)
  if username:
    auth_string = base64.encodestring(username + ':' + password).replace('\n', '')
    request.add_header('Authorization', 'Basic ' + auth_string)
  response = urlopen(request)
  return response

def http_post(url, username='', password='', data={}):
  request = Request(url, urlencode(data))
  if username:
    auth_string = base64.encodestring(username + ':' + password).replace('\n', '')
    request.add_header('Authorization', 'Basic ' + auth_string)
  response = urlopen(request)
  return response
  

class V1Error(Exception): pass

class V1AssetNotFoundError(V1Error): pass


class V1Server(object):
  "Accesses a V1 HTTP server as a client of the XML API protocol"
  
  def __init__(self, address='localhost', instance='VersionOne.Web', username='', password=''):
    self.address = address
    self.instance = instance    
    self.username = username
    self.password = password
    
  def build_url(self, path, query='', fragment='', params='', port=80):
    path = self.instance + path
    if isinstance(query, dict):
      query = urlencode(query)
    url = urlunparse( ('http', self.address, path, params, query, fragment) )
    return url
    
  def get(self, path, query='', postdata=None):
    url = self.build_url(path, query=query)
    try:
      if postdata is not None:
        response = http_post(url, self.username, self.password, postdata)
      else:
        response = http_get(url, self.username, self.password)
      body = response.read()
      return (None, body)
    except HTTPError, e:
      body = e.fp.read()
      return (e, body)
      
  def get_xml(self, path, query='', postdata=None):
    exception, body = self.get(path, query=query, postdata=postdata)
    document = ElementTree.fromstring(body)
    if exception:
      exception.xmldoc = document
      if exception.code == '404':
        raise V1AssetNotFoundError(exception)
      else:
        ElementTree.dump(exception.xmldoc)
        raise V1Error(exception)
    return document
   
  def get_asset_xml(self, asset_type_name, oid):
    path = '/rest-1.v1/Data/{0}/{1}'.format(asset_type_name, oid)
    return self.get_xml(path)
    
  def get_query_xml(self, asset_type_name, where):
    path = '/rest-1.v1/Data/{0}'.format(asset_type_name)
    whereclause = urlencode({"Where": where})
    path = path + '?' + whereclause
    return self.get_xml(path)
    
  def get_meta_xml(self, asset_type_name):
    path = '/meta.v1/{0}'.format(asset_type_name)
    return self.get_xml(path)
    
  def execute_operation(self, asset_type_name, oid, opname):
    path = '/rest-1.v1/Data/{0}/{1}'.format(asset_type_name, oid)
    query = {'op': opname}
    return self.get_xml(path, query=query, postdata={})        
    

      
      
      
  
      
    
    
    
    


