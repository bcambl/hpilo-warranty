#!/usr/bin/env python
"""
Collects Server information from HP iLO XMLReply and
queries the HP ISEE API for warranty information.

"""

from datetime import datetime, timedelta
import cPickle as pickle
import argparse
import csv
import re

from hpisee.hpisee import *

DEFAULT_COUNTRY = 'US'
ilourl = '/xmldata?item=All'
report_output = 'warranty_results.csv'
cwd = os.path.dirname(os.path.realpath(__file__))


def read_serverlist(serverfile=None):
    try:
        with open(serverfile, 'r') as f:
            servers = f.readlines()
            servers = map(lambda x: x.strip('\n'), servers)
        return servers
    except IOError, e:
        raise e


def get_xmlreplydata(ilo_ip=None, ilo_url=None):
    response = requests.get('http://%s%s' % (ilo_ip, ilo_url))
    response = etree.fromstring(response.text)
    return response


def parse_xmlreplydata(data=None):
    """ Older servers do not have the ProductID available via ilo xmlreply so
    we need get the first part of the product number from the UUID and then
    guess the remaining 4 charatcers ie: <xxxxxxx>-001
    In this example, I and guessing '-001' based on a small sample of systems.
    """
    #FIXME: Need alternative way to find the remaining 4 productid characters.
    parsed = {}
    serialno = data.findall('.//HSI//SBSN')[0].text.strip()
    uuidno = data.findall('.//HSI//UUID')[0].text.strip()
    try:
        # This should succeed on newer Servers (DL Gen8+)
        productno = data.findall('.//HSI//PRODUCTID')[0].text.strip()
    except IndexError:
        # Gen5/6/7 Servers do not provide ProductID via xmlreply.. lets guess!
        productregex = '(.*)%s' % serialno
        guessproduct = re.search(productregex, uuidno)
        if guessproduct:
            productno = guessproduct.group(1) + '-001'
        else:
            productno = 'unknown'
    parsed['serial'] = serialno
    parsed['product'] = productno
    return parsed


def guess_again(entitlements=None):
    """ This function will guess again. (see funtion parse_xmlreplydata)
    I found that older servers seem to use -005, so this is my logical second
    guess. Again, this may vary and may not work for everyone!
    """
    #FIXME: Need alternative way to find the remaining 4 productid characters.
    serial, prodno, country = entitlements
    prodno = re.search('(.*)-001', prodno).group(1) + '-005'
    config['entitlements'] = [serial, prodno, country]
    set_registration()
    war_parse(do_request('warranty'))


def set_registration():
    """ Save registration data. Refresh Registration if older than 1 hour.
    """
    regfile = os.path.join(cwd, 'register.save')
    if not os.path.exists(regfile):
        print('Registering..')
        registration = do_request('register')
        registration['date'] = datetime.now()
        with open(regfile, 'wb') as f:
            pickle.dump(registration, f)
    else:
        with open(regfile, 'rb') as f:
            config['auth'] = pickle.load(f)
        if (datetime.now() - config['auth']['date']) > timedelta(hours=1):
            print('Last Registered > 1 hour ago. Registering..')
            registration = do_request('register')
            registration['date'] = datetime.now()
            config['auth'] = registration
            with open(regfile, 'wb') as f:
                pickle.dump(registration, f)
        else:
            pass  # Re-use registration information


def war_parse(server=None, data=None):
    wstart = data.findall('.//OverallWarrantyStartDate')
    wend = data.findall('.//OverallWarrantyEndDate')
    if wstart:
        with open(report_output, 'ab') as csvfile:
            warwriter = csv.writer(csvfile, delimiter=',',
                                   quoting=csv.QUOTE_MINIMAL)
            warwriter.writerow([server, wstart[0].text, wend[0].text])
    else:
        guess_again(config['entitlements'])


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--file',
                        help='File containing a single ilo IP per line',
                        default=os.path.join(cwd, 'serverlist'))
    parser.add_argument('-c', '--country',
                        help='Specify country (defaults to %s)'
                             % DEFAULT_COUNTRY,
                        default=DEFAULT_COUNTRY)
    args = parser.parse_args()
    country = args.country
    serverlist = read_serverlist(args.file)
    for server in serverlist:
        xmlreply = get_xmlreplydata(server, ilourl)
        querydata = parse_xmlreplydata(xmlreply)
        config['entitlements'] = [(querydata['serial'],
                                  querydata['product'],
                                  country)]
        set_registration()
        war_parse(server, do_request('warranty'))

if __name__ == '__main__':
    main()