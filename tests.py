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
    def test_readserverlistioerror(self):
        self.serverlist = read_serverlist(self.badserverfile)

    def test_getxmlreplydata(self):
        start_testserver()
        for server in self.serverlist:
            self.assertIsInstance(
                get_xmlreplydata(server, ilourl), etree._Element)

    @expect_exception(IOError)
    def test_getxmlreplydataioerror(self):
        self.serverlist = read_serverlist(self.badserverfile)
        for server in self.serverlist:
            self.assertIsInstance(
                get_xmlreplydata(server, ilourl), etree._Element)

    def test_parsexmlreplydata(self):
        self.assertIsInstance(parse_xmlreplydata(self.xmlreply), dict)
        self.assertTrue(len(parse_xmlreplydata(self.xmlreply)) == 2)


if __name__ == '__main__':
    unittest.main()