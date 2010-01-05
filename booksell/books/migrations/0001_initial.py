
from south.db import db
from django.db import models
from books.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Book'
        db.create_table('books_book', (
            ('id', orm['books.Book:id']),
            ('asin', orm['books.Book:asin']),
            ('isbn', orm['books.Book:isbn']),
            ('ean', orm['books.Book:ean']),
            ('title', orm['books.Book:title']),
            ('content', orm['books.Book:content']),
            ('created', orm['books.Book:created']),
            ('modified', orm['books.Book:modified']),
        ))
        db.send_create_signal('books', ['Book'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Book'
        db.delete_table('books_book')
        
    
    
    models = {
        'books.book': {
            'asin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ean': ('django.db.models.fields.CharField', [], {'max_length': '13', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        }
    }
    
    complete_apps = ['books']
