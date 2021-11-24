from django.db import models

# Create your models here.
from django.utils import timezone


class File(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="media")
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Загруженный файл'
        verbose_name_plural = 'Загруженные файлы'
        
