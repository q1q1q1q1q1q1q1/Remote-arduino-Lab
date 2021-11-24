from django.contrib import admin
from .models import File
# Register your models here.


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date')


admin.site.site_title = "Удаленная лаборатория"
admin.site.site_header = "Удаленная лаборатория"