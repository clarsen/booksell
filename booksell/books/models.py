from decimal import Decimal
from django.db import models

from lxml import etree

from amazonecs import lookup, lookup_offers_asin

def convert_to_price(xpelem):
    if not xpelem:
        return float(0)
    else:
        price = xpelem[0].text
        if price.startswith("$"):
            return float(price[1:])
        return None

# Create your models here.
class Book(models.Model):
    asin = models.CharField("ASIN", max_length=20, unique=True,null=True)
    isbn = models.CharField('ISBN', max_length=10, unique=True, null=True)
    ean = models.CharField('EAN', max_length=13, unique=True, null=True)

    location = models.CharField(max_length=255, null=True)

    title = models.CharField(max_length=255, null=True)
    salesrank = models.IntegerField(null =True)
    content_indb = models.TextField(editable = False, null=True)
    created = models.DateTimeField(auto_now_add = True,editable=False)
    modified = models.DateTimeField(auto_now = True,editable=False)

    solddate = models.DateTimeField(null=True)
    price = models.DecimalField(max_digits=6,decimal_places=2,null=True)

    _xmlcontent = None

    def fromxml(self,tree):
        self._xmlcontent = tree

        self.asin = self._xpath("//ecs:ASIN")[0].text
        self.isbn = self._xpath("//ecs:ItemAttributes/ecs:ISBN")[0].text
        self.ean = self._xpath("//ecs:ItemAttributes/ecs:EAN")[0].text
        self.title = self._xpath("//ecs:ItemAttributes/ecs:Title")[0].text
        self.salesrank = int(self._xpath("//ecs:SalesRank")[0].text)

        self.content_indb = etree.tostring(tree)

    @property
    def content(self):
        if self._xmlcontent is None:
            self._xmlcontent = etree.fromstring(self.content_indb)
        return self._xmlcontent

    @property
    def image(self):
        if self._xpath("//ecs:SmallImage/ecs:URL"):
            return self._xpath("//ecs:SmallImage/ecs:URL")[0].text
        else:
            return "http://g-ecx.images-amazon.com/images/G/01/x-site/icons/no-img-sm._V47056216_.gif"

    @property
    def image_height(self):
        if self._xpath("//ecs:SmallImage/ecs:URL"):
            return int(self._xpath("//ecs:SmallImage/ecs:Height")[0].text)
        else:
            return 40

    @property
    def image_width(self):
        if self._xpath("//ecs:SmallImage/ecs:URL"):
            return int(self._xpath("//ecs:SmallImage/ecs:Width")[0].text)
        else:
            return 60

    @property
    def author_list(self):
        return [e.text for e in self._xpath("//ecs:ItemAttributes/ecs:Author")]

    @property
    def authors(self):
        lst = self.author_list
        if not lst:
            return ""
        if len(lst) == 1:
            return lst[0]
        else:
            end = lst[-1]
            other = lst[:-1]
            return ', '.join(other) + " and " + end

    @property
    def list_price(self):
        return self._price_from_path("//ecs:ItemAttributes/ecs:ListPrice/ecs:FormattedPrice")

    @property
    def used_price(self):
        return self._price_from_path("//ecs:OfferSummary/ecs:LowestUsedPrice/ecs:FormattedPrice")

    @property
    def new_price(self):
        return self._price_from_path("//ecs:OfferSummary/ecs:LowestNewPrice/ecs:FormattedPrice")

    @property
    def amazon_price(self):
        return self._price_from_path("//ecs:Offers/ecs:Offer/ecs:OfferListing/ecs:Price/ecs:FormattedPrice")

    @property
    def detail_page(self):
        return self._xpath("//ecs:DetailPageURL")[0].text

    @property
    def offer_pages(self):
        return int(self._xpath("//ecs:Offers/ecs:TotalOfferPages")[0].text)

    _alloffers = None
    def alloffers(self):
        if self._alloffers != None:
            return self._alloffers
        res = []
        for i in range(1,self.offer_pages+1):
            xml = lookup_offers_asin(self.asin,i)
            res.append(xml)
        self._alloffers = res
        return res

    def update_offers(self):
        NSMAP = {'ecs' : self.content.nsmap[None]}
        seen = {}
        for oxml in self.alloffers():
            offers = oxml.xpath("//ecs:Offers/ecs:Offer", namespaces = NSMAP)
            for o in offers:
                offer = Offer()
                offer.fromxml(o)
                offer.book = self
                found = False
                try:
                    x = Offer.objects.get(listing_id = offer.listing_id)
                    found = True
                except:
                    pass
                seen[offer.listing_id] = 1
                if not found:
                    #print "ADDING",offer.listing_id
                    offer.save()
                else:
                    #print "UPDATING",offer.listing_id
                    offer = x
                    offer.fromxml(o)
                    offer.save()
                    
        for o in self.offer_set.all():
            if not seen.has_key(o.listing_id):
                #print "NO LONGER ACTIVE",o.listing_id
                o.active = 0
                o.save()

    _distribution = None
    def distribution(self):
        if self._distribution != None:
            return self._distribution

        bycond = {}
        for o in self.offer_set.all():
            if o.active:
                cond = "%s/%s" % (o.condition, o.subcondition)
                if not bycond.has_key(cond):
                    bycond[cond] = []
                bycond[cond].append(float(o.price))

        from stats import quantile
        dist = {}
        for k in bycond.keys():
            if len(bycond[k]) > 1:
                min = quantile(bycond[k],0)
                p25 = quantile(bycond[k],0.25)
                med = quantile(bycond[k],0.5)
                p75 = quantile(bycond[k],0.75)
                max = quantile(bycond[k],1)
                #print k,"N=%d, %03.2f<< %03.2f - %03.2f - %03.2f >>%03.2f" % (len(bycond[k]),min,p25,med,p75,max)
                dist[k] = (len(bycond[k]),Decimal("%3.2f" % min), Decimal("%3.2f" % p25), Decimal("%3.2f" % med), Decimal("%3.2f" % p75), Decimal("%3.2f" % max))
            else:
                #print k,"%03.2f" % bycond[k][0]
                dist[k] = (1,"","",Decimal("%3.2f" % bycond[k][0]),"","")
        self._distribution = dist
        return dist

    def _price_from_path(self, path):
        p = self._xpath(path)
        return convert_to_price(p)

    def _xpath(self, path):
        NSMAP = {'ecs' : self.content.nsmap[None]}
        return self.content.xpath(path, namespaces = NSMAP)

    def migrate(self):
        xml = lookup(self.asin,"ASIN")
        if xml != None:
            self.fromxml(xml)
            self.save()

def lookup_book(book_id, id_type):
    try:
        e = lookup(book_id, id_type)
        if e != None:
            b = Book()
            b.fromxml(e)
            return b
        else:
            return None
    except ValueError:
        return None

class Offer(models.Model):
    book = models.ForeignKey(Book)
    listing_id = models.CharField(max_length=1024, unique=True)

    price = models.DecimalField(max_digits=6,decimal_places=2,editable=False)
    seller_id =  models.CharField(max_length=20)

    condition =  models.CharField(max_length=20)
    subcondition =  models.CharField(max_length=20)

    created = models.DateTimeField(auto_now_add = True,editable=False)
    modified = models.DateTimeField(auto_now = True,editable=False)
    active = models.IntegerField(default=0)

    content_indb = models.TextField(editable = False, null=True)

    def fromxml(self,o):
        NSMAP = {'ecs' : o.nsmap[None]}
        self.listing_id = o.xpath("ecs:OfferListing//ecs:OfferListingId", namespaces = NSMAP)[0].text
        self.price = Decimal(str(convert_to_price(o.xpath("ecs:OfferListing//ecs:FormattedPrice", namespaces = NSMAP))))
        self.seller_id = o.xpath("ecs:Merchant//ecs:MerchantId", namespaces = NSMAP)[0].text
        self.condition = o.xpath("ecs:OfferAttributes//ecs:Condition", namespaces = NSMAP)[0].text
        self.subcondition = o.xpath("ecs:OfferAttributes//ecs:SubCondition", namespaces = NSMAP)[0].text
        self.active = 1
        self.content_indb = etree.tostring(o)
