__author__ = 'bcambl'

from requests.exceptions import ConnectionError
import unittest

from hpilowar import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.serverfile = os.path.join(BASEDIR, 'serverlist.example')
        xmlreply = open(os.path.join(BASEDIR, 'samples/iloxmlreply.xml'))
        self.xmlreply = etree.parse(xmlreply)
        self.serverlist = read_serverlist(self.serverfile)

    def test_readserverlist(self):
        self.assertIsNotNone(self.serverlist)
        self.assertIsInstance(self.serverlist, list)
        self.assertTrue(len(self.serverlist) >= 1)
        for server in self.serverlist:
            self.assertEqual(server, server.strip('\n'))

    def test_getxmlreplydata(self):
        try:
            for server in self.serverlist:
                self.assertIsInstance(
                    get_xmlreplydata(server), etree._Element)
        except ConnectionError:
            print('Warning: Unable to test get_xmlreplydata.')
            print("Run: 'python -m SimpleHTTPServer 8080' "
                  "in project directory and re-run tests")
            self.assertRaises(ConnectionError)


    def test_parsexmlreplydata(self):
        self.assertIsInstance(parse_xmlreplydata(self.xmlreply), dict)
        self.assertTrue(len(parse_xmlreplydata(self.xmlreply)) == 2)


if __name__ == '__main__':
    unittest.main()