#!/usr/bin/env python
# encoding: utf-8
"""
halfcom.py

Created by Case Larsen on 2010-01-17.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import unittest

from mechanize import Browser
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

import re, string

class HalfCom:
    def __init__(self):
        pass

# scrape last order/price info
# http://inventory.half.ebay.com/ws/web/HalfInventoryManagement?imd=reprice&tg=manage-inventory&fcpg=1&pg=1&fhpg=1&m=books&nr=25
# http://inventory.half.ebay.com/ws/web/HalfInventoryManagement?imd=reprice&tg=manage-inventory&fcpg=2&pg=2&fhpg=2&m=books&nr=25&gotopage=2

def lookup_offers_isbn(item_id):
    offers = []
    br = Browser()
    res = br.open("http://books.half.ebay.com/ws/web/HalfISBNSearch?isbn=%s" % item_id)
    soup = BeautifulSoup(res.read())
    ratings = soup.findAll('span',{'class': 'Header'})
    for r in ratings:
        rating = r.text
        prices= r.parent.parent.parent.findNextSibling('table').findAll('tr')[1:]
        linktext  = r.parent.parent.parent.findNextSiblings('table')[1].find(text=re.compile('View all.*'))
        if linktext:
            all = linktext.parent['href']
            # get link
            res2 = br.open(all)
            soup = BeautifulSoup(res2.read())
            rating2 = soup.findAll('span',{'class': 'Header'})
            prices = rating2[0].parent.parent.parent.parent.findAll('table')[3].findAll('tr')[1:]
        for row in prices:
            m = re.search("itemid=(\d+)",row.find('a',href=re.compile("itemid=\d+"))['href'])
            itemid=m.group(1)
            seller = row.find('a',{'class':'SellerDisplayLink'}).text
            price = row.find('span',{'class':'ItemPrice'}).text
            price = string.replace(price,",","")
            if price.startswith("$"):
                price = price[1:]
            offers.append({ 'rating' : rating, 'seller' : seller, 'listing_id' : itemid, 'price' : str(price) })
            print rating,seller,itemid,price
    return offers

class HalfComTests(unittest.TestCase):
    def setUp(self):
        pass
    def testScrape1(self):
        import re
        br = Browser()
        # http://books.half.ebay.com/ws/web/HalfISBNSearch?isbn=9781565920903 -> halfbook-test1.html
        res = br.open_local_file("halfbook-test1.html")
        soup = BeautifulSoup(res.read())
        ratings = soup.findAll('span',{'class': 'Header'})
        for r in ratings:
            rating = r.text
            prices= r.parent.parent.parent.parent.findAll('table')[1].findAll('tr')[1:]
            all   = r.parent.parent.parent.parent.findAll('table')[2].find(text=re.compile('View all.*')).parent['href']
            # get link
            if rating == 'Brand New':
                res = br.open_local_file("halfbook-test1-allbrandnewitems.html")
                soup = BeautifulSoup(res.read())
                rating2 = soup.findAll('span',{'class': 'Header'})
                prices = rating2[0].parent.parent.parent.parent.findAll('table')[3].findAll('tr')[1:]
                for row in prices:
                    m = re.search("itemid=(\d+)",row.find('a',href=re.compile("itemid=\d+"))['href'])
                    itemid=m.group(0)
                    seller = row.find('a',{'class':'SellerDisplayLink'}).text
                    price = row.find('span',{'class':'ItemPrice'}).text
                    print rating,seller,itemid,price

if __name__ == '__main__':
    unittest.main()