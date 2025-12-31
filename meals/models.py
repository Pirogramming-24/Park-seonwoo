from django.db import models

# Create your models here.
class DinnerRecord(models.Model):
    category = models.CharField(max_length=50)
    menu = models.CharField(max_length=50)
    def __str__(self):
        return f"[{self.category}] {self.menu}"