"""
UnitTest Test Suite for hpilo-warranty
--------------------------------------
Notes:
- Python SimpleHTTPServer is used for testing requests
- Uses example files from the examples directory for testing
"""
#TODO: write better tests

import SimpleHTTPServer
from BaseHTTPServer import HTTPServer
import threading
import unittest

from checkwarranty import *

port = 8080
ilourl = ':%s/examples/iloxmlreply.xml' % port


class TestServer(HTTPServer):
    allow_reuse_address = True


def start_testserver():
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = TestServer(("", port), handler)
    httpd_thread = threading.Thread(target=httpd.serve_forever)
    httpd_thread.setDaemon(True)
    httpd_thread.start()


def expect_exception(exception):
    """ Marks test to expect the specified exception.
    Call assertRaises internally
    """
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return test_decorated
    return test_decorator


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.serverfile = os.path.join(cwd, 'examples/serverlist.example')
        self.badserverfile = os.path.join(cwd, 'examples/serverlist.fail')
        xmlreply = open(os.path.join(BASEDIR,
                                     'examples/warranty-ok.xml'))
        self.xmlreply = etree.parse(xmlreply)
        self.serverlist = read_serverlist(self.serverfile)

    def tearDown(self):
        pass

    def test_readserverlist(self):
        self.assertIsNotNone(self.serverlist)
        self.assertIsInstance(self.serverlist, list)
        self.assertTrue(len(self.serverlist) >= 1)
        for server in self.serverlist:
            self.assertEqual(server, server.strip('\n'))

    @expect_exception(IOError)
    def test_readserverlist_ioerror(self):
        self.serverlist = read_serverlist(self.badserverfile)

    def test_getxmlreplydata(self):
        start_testserver()
        for server in self.serverlist:
            self.assertIsInstance(
                get_xmlreplydata(server, ilourl), etree._Element)

    def test_getxmlreplydata_badhost(self):
        self.assertEqual(get_xmlreplydata('badhost', ilourl), 'badhost')

    @expect_exception(IOError)
    def test_getxmlreplydata_ioerror(self):
        self.serverlist = read_serverlist(self.badserverfile)
        for server in self.serverlist:
            self.assertIsInstance(
                get_xmlreplydata(server, ilourl), etree._Element)

    def test_parsexmlreplydata(self):
        xmlreply = get_xmlreplydata('localhost', ilourl)
        self.assertIsInstance(parse_xmlreplydata(xmlreply), dict)

    def test_parsexmlreplydata_badhost(self):
        xmlreply = get_xmlreplydata('badhost', ilourl)
        self.assertIsInstance(parse_xmlreplydata(xmlreply), dict)
        self.assertEqual(parse_xmlreplydata(xmlreply),
                         {'serial': 'unknown', 'product': 'unknown'})

    def test_parsexmlreplydata_noproduct(self):
        xmlreplydata = get_xmlreplydata('localhost', ilourl)
        remproduct = xmlreplydata.xpath('//PRODUCTID')
        remproduct[0].getparent().remove(remproduct[0])
        self.assertIsInstance(xmlreplydata, etree._Element)
        self.assertEqual(parse_xmlreplydata(xmlreplydata),
                         {'serial': 'CZ10130050', 'product': '519841-001'})

    def test_guessagain_001(self):
        config['server'] = None
        config['entitlements'] = [('CZ10130050', '519841-001', 'EU',)]
        guess = guess_again(config['entitlements'])
        self.assertEqual(guess, [('CZ10130050', '519841-005', 'EU',)])

    def test_guessagain_005(self):
        config['server'] = None
        config['entitlements'] = [('CZ10130050', '519841-005', 'EU',)]
        guess = guess_again(config['entitlements'])
        self.assertEqual(guess, [('CZ10130050', 'unknown', 'EU',)])


if __name__ == '__main__':
    unittest.main()