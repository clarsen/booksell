import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from books.models import update_books

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--verbose', action='store_true', dest='verbose',
            help = 'Verbose mode for you control freaks'),
    )
    help = """Get new provider reviews."""
    args = ""
    
    
    def _log(self, msg, error=False):
        if self._verbose or error:
            print msg
    
    def handle(self, *args, **options):
        # handle command-line options
        self._verbose = options.get('verbose', False)
        
        if len(args) == 0:
            pass
        else:
            self._log("ERROR - Takes no args. %d were supplied." % len(args), error=True)
            sys.exit(1)

        update_books()
        return
