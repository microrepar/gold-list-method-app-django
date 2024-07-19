from django.contrib import admin

from goldlistmethod.models import SentenceLabel, SentenceTranslation


class SentenceTranslationAdmin(admin.ModelAdmin):
    list_display = ('foreign_language_sentence', 'mother_language_sentence', 
                    'foreign_language_idiom', 'mother_language_idiom')
    list_display_links = ('foreign_language_sentence', 'mother_language_sentence', 
                          'foreign_language_idiom', 'mother_language_idiom')
    ordering = ('foreign_language_sentence',)


class SentenceLabelAdmin(admin.ModelAdmin):
    list_display = ('sentencetranslation', 'pagesection', 'created_at', 'translation', 'memorialized')

admin.site.register(SentenceTranslation, SentenceTranslationAdmin)
admin.site.register(SentenceLabel, SentenceLabelAdmin)