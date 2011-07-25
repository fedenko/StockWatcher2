from django.db import models
from django.contrib.sessions.models import Session

class Stocks(models.Model):
    session = models.ForeignKey(Session)
    symbol = models.CharField(max_length=10)
    
    def __unicode__(self):
        return '%s | %s' % (self.session.pk, self.symbol)
