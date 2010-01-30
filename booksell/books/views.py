from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, get_list_or_404
from django.template import Context, Template, RequestContext, loader
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from books.models import Book, lookup_book, Condition, ConditionForBook
from books.models import BookForm
from django.forms.models import modelformset_factory

from tagging.models import Tag, TaggedItem

from datetime import datetime

from lxml import etree

# Create your views here.
def index(request):
    books = Book.objects.filter(solddate__isnull = True).order_by("salesrank").all()
    if False:
        for b in books:
            set_up_dist(b)

    return render_to_response('index.html', \
        { 'books' : books}, \
        context_instance=RequestContext(request))

def index_sold(request):
    books = Book.objects.filter(solddate__isnull = False).order_by("-solddate").all()
    return render_to_response('index.html', \
        { 'books' : books}, \
        context_instance=RequestContext(request))

def bulk_update(request):
    BookFormSet = modelformset_factory(Book, fields=['title','location','condition', 'oldprice', 'price'], extra=0)
    if request.method == 'POST':
        formset = BookFormSet(request.POST)
        if formset.is_valid():
            print "valid"
            updated = formset.save()
            if request.POST.get('submit',None) == "Update":
                for b in updated:
                    if b.halfid:
                        from booksell.production import EBAY_DEVID, EBAY_APPID, EBAY_CERTID, EBAY_XML_GATEWAY, EBAY_XML_DIR,EBAY_TOKEN
                        from ebay import EbaySession
                        ebay = EbaySession(EBAY_DEVID,EBAY_APPID,EBAY_CERTID,EBAY_XML_GATEWAY,EBAY_XML_DIR,EBAY_TOKEN)
                        res = ebay.reviseItem(id= b.id, isbn = b.isbn, price=str(b.price), condition = b.condition, comments= b.condition_note)
                        request.user.message_set.create(message="Updated %s at half.com" % b.title)
            elif request.POST.get('submit',None) == "Post to half.com":
                for b in Book.objects.filter(solddate__isnull = True, halfid__isnull = True).all():
                    if str(b.price) != 'None' and str(b.condition) != 'None':
                        print "would post",b.title,' %s/%s to half.com' % (str(b.price),b.condition)
                        from booksell.production import EBAY_DEVID, EBAY_APPID, EBAY_CERTID, EBAY_XML_GATEWAY, EBAY_XML_DIR,EBAY_TOKEN
                        from ebay import EbaySession
                        ebay = EbaySession(EBAY_DEVID,EBAY_APPID,EBAY_CERTID,EBAY_XML_GATEWAY,EBAY_XML_DIR,EBAY_TOKEN)
                        res = ebay.addItem(id= b.id, isbn = b.isbn, price=str(b.price), condition = b.condition, comments= b.condition_note)
                        b.halfid = res['halfid']
                        b.price = str(b.price)  # hack
                        request.user.message_set.create(message="Posted %s to half.com" % b.title)
                        b.save()
            # do something.
            books = Book.objects.filter(solddate__isnull = True).order_by('location','title')
            for b in books:
                if b.condition != None:
                    set_up_dist(b,b.condition)
            formset = BookFormSet(queryset = books)
        else:
            print "was not valid"
    else:
        books = Book.objects.filter(solddate__isnull = True).order_by('location','title')
        for b in books:
            if b.condition != None:
                prices = b.pricelist_for_half(b.condition)
                print 'price',b.title
                if len(prices) >= 4:
                    already = False
                    for p,seller in prices[:4]:
                        print "  price",p,"seller",seller
                        if str(seller) == 'junshinco':
                            already = True
                    if not already:
                        p,s = prices[3]
                        newprice = p - .01
                        print '  update price',newprice
                        b.update_price(newprice)
                set_up_dist(b,b.condition)

        formset = BookFormSet(queryset = books)

    return render_to_response('bulk_update.html', \
        { 'formset' : formset}, \
        context_instance=RequestContext(request))

def set_up_dist(b,cond=None):
    d = b.distribution()
    if d.has_key('LIKE_NEW'):
        if not cond or cond == 'LIKE_NEW':
            b.mint_n,b.mint_min,b.mint_p25,b.mint_med,b.mint_p75,b.mint_max = d['LIKE_NEW']
    if d.has_key('VERY_GOOD'):
        if not cond or cond == 'VERY_GOOD':
            b.vg_n,b.vg_min,b.vg_p25,b.vg_med,b.vg_p75,b.vg_max = d['VERY_GOOD']
    if d.has_key('GOOD'):
        if not cond or cond == 'GOOD':
            b.g_n,b.g_min,b.g_p25,b.g_med,b.g_p75,b.g_max = d['GOOD']
    if d.has_key('ACCEPTABLE'):
        if not cond or cond == 'ACCEPTABLE':
            b.a_n,b.a_min,b.a_p25,b.a_med,b.a_p75,b.a_max = d['ACCEPTABLE']
    dh = b.distribution_for_half()
    if dh.has_key('LIKE_NEW'):
        if not cond or cond == 'LIKE_NEW':
            b.h_mint_n,b.h_mint_min,b.h_mint_p25,b.h_mint_med,b.h_mint_p75,b.h_mint_max = dh['LIKE_NEW']
    if dh.has_key('VERY_GOOD'):
        if not cond or cond == 'VERY_GOOD':
            b.h_vg_n,b.h_vg_min,b.h_vg_p25,b.h_vg_med,b.h_vg_p75,b.h_vg_max = dh['VERY_GOOD']
    if dh.has_key('GOOD'):
        if not cond or cond == 'GOOD':
            b.h_g_n,b.h_g_min,b.h_g_p25,b.h_g_med,b.h_g_p75,b.h_g_max = dh['GOOD']
    if dh.has_key('ACCEPTABLE'):
        if not cond or cond == 'ACCEPTABLE':
            b.h_a_n,b.h_a_min,b.h_a_p25,b.h_a_med,b.h_a_p75,b.h_a_max = dh['ACCEPTABLE']
    
def editbook(request,id):
    b = get_object_or_404(Book,asin=id)
    set_up_dist(b)
    book_conds = ConditionForBook.objects.filter(book = b).all()

    if request.method == 'POST':
        if request.POST.get('submit',None) == "Update Price and Condition":
            b.price = request.POST.get('price',None)
            b.location = request.POST.get('location',None)
            b.condition = request.POST.get('condition',None)
            request.user.message_set.create(message="Updated %s" % b.title)
        elif request.POST.get('submit',None) == "Update":
            #print "would update",b.halfid,"on Half.com"
            from booksell.production import EBAY_DEVID, EBAY_APPID, EBAY_CERTID, EBAY_XML_GATEWAY, EBAY_XML_DIR,EBAY_TOKEN
            from ebay import EbaySession
            ebay = EbaySession(EBAY_DEVID,EBAY_APPID,EBAY_CERTID,EBAY_XML_GATEWAY,EBAY_XML_DIR,EBAY_TOKEN)
            res = ebay.reviseItem(id= b.id, isbn = b.isbn, price=str(b.price), condition = b.condition, comments= b.condition_note)
            b.price = str(b.price)  # hack
            request.user.message_set.create(message="Updated %s at half.com" % b.title)
        elif request.POST.get('submit',None) == "Post":
            #print "post to Half.com"
            from booksell.production import EBAY_DEVID, EBAY_APPID, EBAY_CERTID, EBAY_XML_GATEWAY, EBAY_XML_DIR,EBAY_TOKEN
            from ebay import EbaySession
            ebay = EbaySession(EBAY_DEVID,EBAY_APPID,EBAY_CERTID,EBAY_XML_GATEWAY,EBAY_XML_DIR,EBAY_TOKEN)
            res = ebay.addItem(id= b.id, isbn = b.isbn, price=str(b.price), condition = b.condition, comments= b.condition_note)
            b.halfid = res['halfid']
            b.price = str(b.price)  # hack
            request.user.message_set.create(message="Posted %s to half.com" % b.title)
        b.save()
    form = BookForm(instance=b)
    tags = ['cover','spine', 'edge','pages','"other conditions"','extras','"generic age"','shipping',]
    return render_to_response('book_detail.html', \
        { 'book' : b, 'book_conds' : book_conds, 'form' : form, 'tags' : tags }, \
        context_instance=RequestContext(request))

def add_condition(request,bookid,conditionid):
    b = get_object_or_404(Book,id=bookid)
    c = get_object_or_404(Condition,id=conditionid)
    b.add_condition(c)
    # redirect to same page
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def remove_condition(request,bookcondid):
    bc = get_object_or_404(ConditionForBook,id=bookcondid)
    bc.book.remove_condition(bc.condition)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def move_condition(request,bookcondid,dir):
    bc = get_object_or_404(ConditionForBook,id=bookcondid)
    book_conds = ConditionForBook.objects.filter(book = bc.book).all()
    dir=int(dir)
    if dir < 0:
        bc.order = bc.order-1
    else:
        bc.order = bc.order+1
    for b in book_conds:
        if b.order == bc.order:
            if dir < 0:
                b.order = b.order+1
            else:
                b.order = b.order-1
            b.save()
            break
    bc.save()
    # redirect to same page
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

    
def normalize(id,type):
    if str(type.lower()) == 'upc' or str(type.lower()) == 'ean':
        if len(id) == 18:
            return id[0:13]
    return id

def conditions(request):
    from tagging.models import Tag
    tags = Tag.objects.usage_for_model(Condition)
    seen = {}
    for t in tags:
        conds = TaggedItem.objects.get_by_model(Condition.objects.filter(picklist=1).order_by("conditionnote"), t)
        for c in conds:
            seen[c.id] = 1
    untagged_conds = []
    for c in Condition.objects.filter(picklist=1).order_by("conditionnote"):
        if not seen.has_key(c.id):
            untagged_conds.append(c)

    return render_to_response('conditions.html', \
            { 'tags' : tags,  \
             'untagged_conds' : untagged_conds }, \
            context_instance=RequestContext(request))

def condition_status(request,id,status):
    c = get_object_or_404(Condition,id=id)
    c.picklist = status
    c.save()
    return HttpResponseRedirect(reverse('books.views.conditions'))

def condition_edit(request,id):
    cond = get_object_or_404(Condition,id=id)
    if request.method == 'POST':
        if request.POST.get('submit',None) == "Update":
            cond.conditionnote = request.POST.get('condition_note',None)
            cond.tags = request.POST.get('condition_tags',None)
            request.user.message_set.create(message="Updated")
            cond.save()
            return HttpResponseRedirect(reverse('books.views.conditions'))

    return render_to_response('condition_edit.html', \
            { 'cond' : cond}, \
            context_instance=RequestContext(request))

def condition_ignore(request,id):
    conds = Condition.objects.filter(ignore = 0).order_by("-picklist","conditionnote").all()
    for c in conds:
        if int(c.picklist) == 0:
            print "ignoring",c.id
            c.ignore = 1
            c.save()
        if int(c.id) == int(id):
            break
    return HttpResponseRedirect(reverse('books.views.conditions'))


def asxml(request,id):
    b = get_object_or_404(Book,asin=id)
    books = Book.objects.all()
    for b in books:
        print "checking",b.title
        desc = []
        for o in b.offer_set.all():
            if o.content_indb != None:
                desc.extend(o.descriptions)
    print len(desc), 'descriptions'

    for d in desc:
        c,created = Condition.objects.get_or_create(conditionnote=d)
        if not created:
            c.count = c.count+1
            c.save()

    return render_to_response('conditions.html', \
            { 'desc' : desc}, \
            context_instance=RequestContext(request))

    #b.update_offers()
    #b.distribution()
    return HttpResponse("", mimetype='application/xml')

    res = "<all>\n"
    res = res + b.content_indb
    for o in b.alloffers():
        res = res + "\n" + etree.tostring(o)
    res = res + "\n</all>\n"
    b.distribution()
    return HttpResponse(res, mimetype='application/xml')

def deletebook(request,id):
    b = get_object_or_404(Book,asin=id)
    b.delete()
    return HttpResponseRedirect(reverse('books.views.index'))

def soldbook(request,id):
    b = get_object_or_404(Book,asin=id)
    if request.method == 'POST':
        b.price = request.POST.get('price',None)
        b.solddate = request.POST.get('solddate',datetime.now())
        b.shipping = request.POST.get('shipping',None)
        b.total_rev = request.POST.get('total_rev',None)
        b.save()
        request.user.message_set.create(message="Sold %s" % b.title)
        return HttpResponseRedirect(reverse('books.views.index'))
    else:
        if b.solddate == None:
            b.solddate = datetime.now()
        return render_to_response('book_sold.html', \
            { 'book' : b}, \
            context_instance=RequestContext(request))


def add(request):
    if request.method == 'POST':
        #print request
        bookids = request.POST.get('book_id','').strip().splitlines()
        type = request.POST.get('id_type','')
        for b in bookids:
            q = {}
            b = normalize(b,type)
            if str(type.lower()) == 'upc':
                q['ean'] = b
            else:
                q[str(type.lower())] = b
            if list(Book.objects.filter(**q)):
                request.user.message_set.create(message="Book %s already exists" % b)
            else:
                print "would add",type,b
        
                book = lookup_book(b,type)
                if book:
                    request.user.message_set.create(message="Added %s (%s)" % (b, book.title))
                    book.location = request.POST.get('location','').strip()
                    book.save()
                    book.update_offers()
                else:
                    request.user.message_set.create(message="%s not found" % b)
        return HttpResponseRedirect(reverse('books.views.index'))
#        return HttpResponseRedirect(reverse('books.views.index'))
        
    return render_to_response('index.html', \
        { 'books' : []}, \
        context_instance=RequestContext(request))

add = permission_required('books.add_book')(add)
