from __future__ import unicode_literals

from django.db import models
from jsonfield import JSONField

# Create your models here.

class Graph(models.Model):
    name = models.CharField(max_length=200)
    data = JSONField(default='{}', blank=True, null=True)
        
    def __str__(self):
        return self.name
        
class Infection(models.Model):
    graph = models.ForeignKey('Graph', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    data = JSONField(default='{}', blank=True, null=True)
        
    def __str__(self):
        return self.name
