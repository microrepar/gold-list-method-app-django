from django.contrib import admin

from goldlistmethod.models import Notebook


class NotebookAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'foreign_idiom', 'mother_idiom')
    list_display_link = ('name', 'user', 'foreign_idiom', 'mother_idiom')
    list_editable = ('user',)


admin.site.register(Notebook, NotebookAdmin)