from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, get_list_or_404
from django.template import Context, Template, RequestContext, loader
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from books.models import Book, lookup_book

from datetime import datetime

from lxml import etree

# Create your views here.
def index(request):
    books = Book.objects.filter(solddate__isnull = True).order_by("salesrank").all()
    for b in books:
        d = b.distribution()
        if d.has_key('Used/mint'):
            b.mint_n,b.mint_min,b.mint_p25,b.mint_med,b.mint_p75,b.mint_max = d['Used/mint']
        if d.has_key('Used/verygood'):
            b.vg_n,b.vg_min,b.vg_p25,b.vg_med,b.vg_p75,b.vg_max = d['Used/verygood']
        if d.has_key('Used/good'):
            b.g_n,b.g_min,b.g_p25,b.g_med,b.g_p75,b.g_max = d['Used/good']
        if d.has_key('Used/acceptable'):
            b.a_n,b.a_min,b.a_p25,b.a_med,b.a_p75,b.a_max = d['Used/acceptable']

    return render_to_response('index.html', \
        { 'books' : books}, \
        context_instance=RequestContext(request))

def normalize(id,type):
    if str(type.lower()) == 'upc' or str(type.lower()) == 'ean':
        if len(id) == 18:
            return id[0:13]
    return id

def asxml(request,id):
    #b = get_object_or_404(Book,asin=id)
    books = Book.objects.all()
    for b in books:
        print "checking",b.title
        ok = False
        for o in b.offer_set.all():
            if o.content_indb != None:
                ok = True
                break
        if not ok:
            print "updating",b.title
            b.update_offers()

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
        b.save()
        request.user.message_set.create(message="Sold %s" % b.title)
        return HttpResponseRedirect(reverse('books.views.index'))
    else:
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
