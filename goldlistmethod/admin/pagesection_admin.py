from django.contrib import admin
from goldlistmethod.models import PageSection, SentenceLabel


class SentenceLabelTabularInline(admin.TabularInline):
    model = SentenceLabel
    extra = 1

    def get_max_num(self, request, obj=None, **kwargs):
        if obj:
            return obj.notebook.sentence_list_size
        else:
            return super().get_max_num(request, obj, **kwargs)


class PageSectionAdmin(admin.ModelAdmin):
    list_per_page = 5
    
    list_display = ('id', 'notebook', 'page_number', 'group', 'created_at', 'distillation_at', 
                    'distillated', 'distillation_actual', 'created_by')
    list_display_links = ('notebook', 'page_number', 'group', 'distillation_at', 'distillated')
    editable = ('notebook', 'page_number', 'group', 'distillation_at', 'distillated')
    ordering = ('-created_at',)
    inlines = (SentenceLabelTabularInline,)


admin.site.register(PageSection, PageSectionAdmin)

