
from south.db import db
from django.db import models
from books.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Offer'
        db.create_table('books_offer', (
            ('id', orm['books.offer:id']),
            ('book', orm['books.offer:book']),
            ('listing_id', orm['books.offer:listing_id']),
            ('price', orm['books.offer:price']),
            ('seller_id', orm['books.offer:seller_id']),
            ('condition', orm['books.offer:condition']),
            ('subcondition', orm['books.offer:subcondition']),
            ('created', orm['books.offer:created']),
            ('modified', orm['books.offer:modified']),
            ('active', orm['books.offer:active']),
        ))
        db.send_create_signal('books', ['Offer'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Offer'
        db.delete_table('books_offer')
        
    
    
    models = {
        'books.book': {
            'asin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'content_indb': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ean': ('django.db.models.fields.CharField', [], {'max_length': '13', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'salesrank': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'books.offer': {
            'active': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['books.Book']"}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listing_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'seller_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subcondition': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }
    
    complete_apps = ['books']
