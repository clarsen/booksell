
from south.db import db
from django.db import models
from books.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Book.content_indb'
        db.add_column('books_book', 'content_indb', orm['books.book:content_indb'])
        
        # Deleting field 'Book.content'
        db.delete_column('books_book', 'content')
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Book.content_indb'
        db.delete_column('books_book', 'content_indb')
        
        # Adding field 'Book.content'
        db.add_column('books_book', 'content', orm['books.book:content'])
        
    
    
    models = {
        'books.book': {
            'asin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'content_indb': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ean': ('django.db.models.fields.CharField', [], {'max_length': '13', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        }
    }
    
    complete_apps = ['books']
