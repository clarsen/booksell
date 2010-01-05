from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('books.views.index'))
