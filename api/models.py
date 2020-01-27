from django.db import models

class localBooks(models.Model):
	title = models.CharField(max_length=200)
	authors = models.CharField(max_length=200)
	issued = models.BooleanField(default=False)