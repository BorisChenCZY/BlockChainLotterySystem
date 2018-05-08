from django.contrib import admin

from . import models

class Article_admin(admin.ModelAdmin):
    list_display = ('title','content','pub_time')
    list_filter = ('pub_time', )


admin.site.register(models.Artivle,Article_admin)
