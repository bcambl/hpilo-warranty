#!/usr/bin/env python
"""
Collects Server information from HP iLO XMLReply and
queries the HP ISEE API for warranty information.

"""

DEBUG = True

from lxml import etree
import requests
import argparse
import os

BASEDIR = os.path.dirname(os.path.realpath(__file__))

ilourl = '/xmldata?item=All'
if DEBUG:
    ilourl = ':8080/samples/iloxmlreply.xml'


def read_serverlist(serverfile=None):
    with open(serverfile, 'r') as f:
        servers = f.readlines()
        servers = map(lambda x: x.strip('\n'), servers)
    return servers


def get_xmlreplydata(ilo_ip=None):
    response = requests.get('http://%s%s' % (ilo_ip, ilourl))
    response = etree.fromstring(response.text)
    return response


def parse_xmlreplydata(data=None):
    parsed = {}
    serialno = data.findall('.//HSI//SBSN')[0].text
    productno = data.findall('.//HSI//PRODUCTID')[0].text
    parsed['serial'] = serialno
    parsed['product'] = productno
    return parsed


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--file',
                        help='File containing a single ilo IP per line',
                        default=os.path.join(BASEDIR, 'serverlist'))
    args = parser.parse_args()
    serverlist = read_serverlist(args.file)
    for server in serverlist:
        xmlreply = get_xmlreplydata(server)
        querydata = parse_xmlreplydata(xmlreply)
        print querydata


if __name__ == '__main__':
    main()