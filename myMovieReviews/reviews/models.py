from django.db import models

class Review(models.Model) :
  title = models.CharField(max_length=100)
  director = models.CharField(max_length=32)
  main_actor = models.CharField(max_length=32)
  genre = models.CharField(max_length=32)
  rating = models.FloatField()
  release_year = models.IntegerField()
  runtime = models.IntegerField()
  content = models.TextField() 
  created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
        return self.title