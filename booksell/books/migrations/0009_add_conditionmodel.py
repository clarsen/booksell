
from south.db import db
from django.db import models
from books.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Condition'
        db.create_table('books_condition', (
            ('id', orm['books.condition:id']),
            ('conditionnote', orm['books.condition:conditionnote']),
            ('count', orm['books.condition:count']),
        ))
        db.send_create_signal('books', ['Condition'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Condition'
        db.delete_table('books_condition')
        
    
    
    models = {
        'books.book': {
            'asin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'content_indb': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ean': ('django.db.models.fields.CharField', [], {'max_length': '13', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2'}),
            'salesrank': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'solddate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'books.condition': {
            'conditionnote': ('django.db.models.fields.TextField', [], {}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'books.offer': {
            'active': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['books.Book']"}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'content_indb': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listing_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'unique': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'seller_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subcondition': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }
    
    complete_apps = ['books']
