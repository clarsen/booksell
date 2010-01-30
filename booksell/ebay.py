#!/usr/bin/env python
# encoding: utf-8
"""
ebay.py

Created by Case Larsen on 2010-01-08.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import unittest
import httplib, ConfigParser, codecs

from lxml import etree



class EbaySession:
    def __init__(self,devid,appid,certid,serverurl,serverdir,usertoken):
        self.devid = devid
        self.appid = appid
        self.certid = certid
        self.serverurl = serverurl
        self.serverdir = serverdir
        self.usertoken = usertoken
        self.compatibilitylevel = 647
        self.siteid = 0
    def _getItem(self,detailLevel,itemid):
        requestXml = """<?xml version='1.0' encoding='utf-8'?>
                  <GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                  <RequesterCredentials><eBayAuthToken>""" \
                  + self.usertoken \
                  + "</eBayAuthToken></RequesterCredentials>"
        if (detailLevel != ""):
          requestXml = requestXml + "<DetailLevel>" + detailLevel + "</DetailLevel>"

        requestXml = requestXml + "<ItemID>" + itemid + "</ItemID></GetItemRequest>"
        return requestXml

    def value(self,xml,elem):
        nsmap = {'ebay' : xml.nsmap[None]}
        return xml.xpath(elem, namespaces = nsmap)[0].text

    def _addItem(self,**kwargs):
        requestXml = """<?xml version='1.0' encoding='utf-8'?>
                  <AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                  <RequesterCredentials><eBayAuthToken>""" \
                  + self.usertoken \
                  + "</eBayAuthToken></RequesterCredentials><DetailLevel>ReturnAll</DetailLevel>"

        # condition is one of:
        #  BRAND_NEW
        #  LIKE_NEW
        #  VERY_GOOD
        #  GOOD
        #  ACCEPTABLE
        # Atrribute id 3822 - seller notes
        # Attribute id 3827 - comments
        # <Description>seller's description</Description>
        requestXml = requestXml + """<Item>
                                        <AttributeArray>
                                        <Attribute attributeLabel="Notes"><Value><ValueLiteral>""" \
                                + kwargs['comments'] \
                                + """</ValueLiteral></Value></Attribute>
                                        <Attribute attributeLabel="Condition"><Value><ValueLiteral>""" \
                                + kwargs['condition'] \
                                + """</ValueLiteral></Value></Attribute>
                                        </AttributeArray>
                                        <StartPrice>""" \
                                + kwargs['price'] \
                                + """</StartPrice>
                                    <Country>US</Country>
                                    <Currency>USD</Currency>
                                    <ExternalProductID><Value>""" \
                                + kwargs['isbn'] \
                                + """</Value><Type>ISBN</Type>
                                    <ReturnSearchResultOnDuplicates>True</ReturnSearchResultOnDuplicates></ExternalProductID>
                                    <ListingDuration>GTC</ListingDuration>
                                    <ListingType>Half</ListingType>
                                    <Location>San Jose, CA</Location>
                                    <Quantity>1</Quantity>
                                    <SellerInventoryID>""" \
                                + str(kwargs['id']) \
                                + """</SellerInventoryID>
                                    </Item>""" \
                            + "</AddItemRequest>"
        return requestXml

    def _reviseItem(self,**kwargs):
        requestXml = """<?xml version='1.0' encoding='utf-8'?>
                  <ReviseItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                  <RequesterCredentials><eBayAuthToken>""" \
                  + self.usertoken \
                  + "</eBayAuthToken></RequesterCredentials><DetailLevel>ReturnAll</DetailLevel>"

        requestXml = requestXml + """<Item>
                                        <AttributeArray>
                                        <Attribute attributeLabel="Notes"><Value><ValueLiteral>""" \
                                + kwargs['comments'] \
                                + """</ValueLiteral></Value></Attribute>
                                <Attribute attributeLabel="Condition"><Value><ValueLiteral>""" \
                                + kwargs['condition'] \
                                + """</ValueLiteral></Value></Attribute>
                                        </AttributeArray>
                                        <StartPrice>""" \
                                + kwargs['price'] \
                                + """</StartPrice>
                                    <Country>US</Country>
                                    <Currency>USD</Currency>
                                    <ExternalProductID><Value>""" \
                                + kwargs['isbn'] \
                                + """</Value><Type>ISBN</Type>
                                    <ReturnSearchResultOnDuplicates>True</ReturnSearchResultOnDuplicates></ExternalProductID>
                                    <ListingDuration>GTC</ListingDuration>
                                    <ListingType>Half</ListingType>
                                    <Location>San Jose, CA</Location>
                                    <Quantity>1</Quantity>
                                    <SellerInventoryID>""" \
                                + str(kwargs['id']) \
                                + """</SellerInventoryID>
                                    </Item>""" \
                            + "</ReviseItemRequest>"
        print "would send",requestXml
        return requestXml

    def buildHttpHeaders(self,verb):
        httpHeaders = {"X-EBAY-API-COMPATIBILITY-LEVEL": self.compatibilitylevel,
                   "X-EBAY-API-DEV-NAME": self.devid,
                   "X-EBAY-API-APP-NAME": self.appid,
                   "X-EBAY-API-CERT-NAME": self.certid,
                   "X-EBAY-API-CALL-NAME": verb,
                   "X-EBAY-API-SITEID": self.siteid,
                   "Content-Type": "text/xml"}
        return httpHeaders

    def addItem(self,**kwargs):
        con = httplib.HTTPSConnection(self.serverurl)
        con.request("POST", self.serverdir, self._addItem(**kwargs), self.buildHttpHeaders("AddItem"))
        response = con.getresponse()
        if response.status != 200:
            print "Error sending request: " + response.reason
            return None
            sys.exit(0)
        else:
            data = response.read()
            print data
            con.close()
            r = etree.fromstring(data)
            id = self.value(r,"//ebay:ItemID")
            return {'halfid' : id }

    def reviseItem(self,**kwargs):
        con = httplib.HTTPSConnection(self.serverurl)
        con.request("POST", self.serverdir, self._reviseItem(**kwargs), self.buildHttpHeaders("ReviseItem"))
        response = con.getresponse()
        if response.status != 200:
            print "Error sending request: " + response.reason
            return None
            sys.exit(0)
        else:
            data = response.read()
            con.close()
            r = etree.fromstring(data)
            print data
            
    def getItem(self,itemid):
        con = httplib.HTTPSConnection(self.serverurl)
        con.request("POST", self.serverdir, self._getItem("ReturnAll",itemid), self.buildHttpHeaders("GetItem"))
        response = con.getresponse()
        if response.status != 200:
            print "Error sending request: " + response.reason
            sys.exit(0)
        else:
            data = response.read()
            con.close()
            print data

sys.path.insert(0,".")
from booksell.production import *

class ebayTests(unittest.TestCase):
    def setUp(self):
        self.t = EbaySession(EBAY_DEVID,EBAY_APPID,EBAY_CERTID,EBAY_XML_GATEWAY,EBAY_XML_DIR,EBAY_TOKEN)
        pass
#    def testAddItem(self):
#        self.t.addItem(id=69, isbn = "1565925254", price="1234.56", condition = "ACCEPTABLE", comments="These are comments.")
    def testGetItem(self):
        self.t.getItem("341365825614")
if __name__ == '__main__':
    unittest.main()