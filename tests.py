__author__ = 'bcambl'

import SimpleHTTPServer
from BaseHTTPServer import HTTPServer
import threading
import unittest

from hpilowar import *


class TestServer(HTTPServer):
    allow_reuse_address = True


def start_testserver():
    port = 8080
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = TestServer(("", port), handler)
    httpd_thread = threading.Thread(target=httpd.serve_forever)
    httpd_thread.setDaemon(True)
    httpd_thread.start()


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.serverfile = os.path.join(BASEDIR, 'serverlist.example')
        xmlreply = open(os.path.join(BASEDIR, 'samples/iloxmlreply.xml'))
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

    def test_getxmlreplydata(self):
        start_testserver()
        for server in self.serverlist:
            self.assertIsInstance(
                get_xmlreplydata(server), etree._Element)

    def test_parsexmlreplydata(self):
        self.assertIsInstance(parse_xmlreplydata(self.xmlreply), dict)
        self.assertTrue(len(parse_xmlreplydata(self.xmlreply)) == 2)


if __name__ == '__main__':
    unittest.main()