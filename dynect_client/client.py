import json
import urllib2
import threading


class DynectDNSClient:
  def __init__(self, customerName, userName, password,
               defaultDomain=None):
    self.customerName = customerName
    self.userName = userName
    self.password = password
    self.defaultDomainName = defaultDomain
    self.sessionToken = None
    self.errors = []
    self.lock = threading.Semaphore()

  def getRecords(self, hostName, type="A", domainName=None):
    if not domainName:
      domainName = self.defaultDomainName

    try:
      if hostName:
        response = self._request('AllRecord/%s/%s/' % (
            domainName, hostName), None)
      else:
        response = self._request('AllRecord/%s/' % (
            domainName), None)

      if not response:
        return []

      if 'data' in response:
        records = []
        for url in response['data']:
          record = self._request(url.replace('/REST/', ''), None)
          record['record'] = record['data']['fqdn']
          record['value'] = record['data']['rdata'].values()[0]
          record['type'] = record['data']['record_type']
          record['ttl'] = record['data']['ttl']
          record['url'] = url

          records.append(record)
      return records
    except urllib2.HTTPError, e:
      if e.code == 404:
        return None
      else:
        import traceback
        self.errors.append(traceback.format_exc())
        return None

  def get_errors(self):
    errors = [e for e in self.errors]
    self.errors = []
    return errors

  def addRecord(self, data, hostName, type="A", TTL=3600, domainName=None):
    url, fieldName = self._api_details(type)

    if not domainName:
      domainName = self.defaultDomainName

    url = "%s/%s/%s/" % (url, domainName, hostName)
    data = {"ttl": str(TTL),
            "rdata": {fieldName: data}}

    response = self._request(url, data)
    if response['status'] != 'success':
      self.errors.append(response)
      return False

    response = self._publish(domainName)
    return True

  def deleteRecord(self, data, hostName, type="A", domainName=None):
    if not domainName:
      domainName = self.defaultDomainName

    records = self.getRecords(hostName, type, domainName)
    if not records:
      self.errors.append("No records exist for %s" % hostName)
      return False

    url = None
    for record in records:
      if record['value'] == data and record['record'] == hostName:
        url = record['url']
        break

    if not url:
      self.errors.append("Tried to delete a record that didn't "
                         "exist (%s,%s)" % (
          data, hostName))
      return False

    url = url.replace("/REST/", "")
    try:
      self._request(url, None, "DELETE")
      self._publish(domainName)
    except:
      import traceback
      self.errors.append(traceback.format_exc())
      return False

    return True

  def _api_details(self, type):
    if type == "A":
      return ("ARecord", "address")
    else:
      return ("CNameRecord", "cname")

  def _publish(self, domainName=None):
    self._request("Zone/%s" % domainName, {"publish": True}, type="PUT")

  def _login(self):
    response = self._request("Session/", {'customer_name': self.customerName,
                                                'user_name': self.userName,
                                                'password': self.password})
    if response['status'] != 'success':
      return
    self.sessionToken = response['data']['token']

  def _request(self, url, post, type=None):
    fullurl = "https://api2.dynect.net/REST/%s" % url

    if post:
      postdata = json.dumps(post)
      req = MethodRequest(fullurl, postdata)
    else:
      req = MethodRequest(fullurl)

    req.add_header('Content-Type', 'application/json')
    req.add_header('Auth-Token', self.sessionToken)
    if type:
      setattr(req, "method", type)

    self.lock.acquire()
    try:
      resp = urllib2.urlopen(req)
      self.lock.release()
      if type:
        return resp
      else:
        return json.loads(resp.read())

    except urllib2.HTTPError, e:
      self.lock.release()
      if e.code == 400:
        self._login()
        return self._request(url, post)
      else:
        self.errors.append(e)
        return None
    except Exception, err:
      self.lock.release()
      import traceback
      self.errors.append(traceback.format_exc())
      return None


class MethodRequest(urllib2.Request):
  def __init__(self, *args, **kwargs):
    urllib2.Request.__init__(self, *args, **kwargs)
    self.method = None

  def get_method(self):
    if self.method:
      return self.method
    return urllib2.Request.get_method(self)
