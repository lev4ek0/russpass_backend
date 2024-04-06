from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Language, Translate, Tag, Photo

class LanguageAdmin(ModelAdmin):
    model = Language
    menu_label = 'Languages'
    menu_icon = 'language'
    list_display = ('name',)
    search_fields = ('name',)

modeladmin_register(LanguageAdmin)

class TranslateAdmin(ModelAdmin):
    model = Translate
    menu_label = 'Translates'
    menu_icon = 'doc-full'
    list_display = ('language', 'text', 'tag')
    search_fields = ('text',)

modeladmin_register(TranslateAdmin)

class TagAdmin(ModelAdmin):
    model = Tag
    menu_label = 'Tags'
    menu_icon = 'tag'
    list_display = ('name',)
    search_fields = ('name',)

modeladmin_register(TagAdmin)

class PhotoAdmin(ModelAdmin):
    model = Photo
    menu_label = 'Photos'
    menu_icon = 'image'
    list_display = ('image',)
    search_fields = ('image',)

modeladmin_register(PhotoAdmin)
