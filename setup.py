from distutils.core import setup

setup(name='dynect-client',
      version='0.2.8',
      description='Dynect REST API Client for adding/removing domains',
      author='Zach Goldberg',
      author_email='zach@zachgoldberg.com',
      url='https://github.com/ZachGoldberg/Dynect-REST-Python-Client',
      packages=[
        'dynect_client',
        ],
      classifiers=['Topic :: Internet :: Name Service (DNS)',
                   'Development Status :: 3 - Alpha'],
      long_description="""
Just a simple wrapper around the Dynect REST API.  There are three important API functions.

  **getRecords** (hostName="foo.mydomain.com")
    Gets all records associated with foo.mydomain.com


  **addRecord** (data="1.2.3.4", hostName="bar.mydomain.com", type="A", TTL=3600)
    Adds a new DNS A Record for bar.mydomain.com of 1.2.3.4


  **deleteRecord** (data="1.2.3.4", hostaName="bar.mydomain.com", type="A")
    Deleted the 1.2.3.4 A record from bar.mydomain.com


>>> import dynect_client
>>> client = dynect_client.DynectDNSClient("mycustomername", "myusername", "mypassword", "mydomain.com")
>>> client.getRecords("foo.mydomain.com")
[{u'status': u'success', u'job_id': 60030085, u'msgs': [{u'INFO': u'get: Found the record', u'SOURCE': u'API-B', u'ERR_CD': None, u'LVL': u'INFO'}], 'value': u'8.8.8.8', 'record': u'foo.mydomain.com', u'data': {u'zone': u'mydomain.com', u'ttl': 600, u'fqdn': u'foo.mydomain.com', u'record_type': u'A', u'rdata': {u'address': u'8.8.8.8'}, u'record_id': 21115048}}, {u'status': u'success', u'job_id': 60030087, u'msgs': [{u'INFO': u'get: Found the record', u'SOURCE': u'API-B', u'ERR_CD': None, u'LVL': u'INFO'}], 'value': u'8.8.4.4', 'record': u'foo.mydomain.com', u'data': {u'zone': u'mydomain.com', u'ttl': 600, u'fqdn': u'foo.mydomain.com', u'record_type': u'A', u'rdata': {u'address': u'8.8.4.4'}, u'record_id': 21115118}}]


"""
     )
