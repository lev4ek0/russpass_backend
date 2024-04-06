from django.db import models
from django.utils.translation import gettext as _
from pgvector.django import VectorField


# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('lang_name'))

    translates: list["Translate"]

    def __str__(self) -> str:
        return f"Language({self.id}, {self.name})"


class Translate(models.Model):
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name="translates")
    text = models.CharField(max_length=255, verbose_name=_('translate_text'))
    tag = models.ForeignKey("Tag", on_delete=models.SET_NULL, null=True, related_name="translates")

    def __str__(self) -> str:
        return f"Translate({self.id}, {self.text})"

class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('tag_name'))
    photo = list["Photo"]

    translates: list[Translate]

    def __str__(self) -> str:
        return f"Tag({self.id}, {self.name})"

class Photo(models.Model):
    image = models.ImageField(
        upload_to='%Y/%m/%d/',
        verbose_name=_('image')
    )
    embeding = VectorField(dimensions=512, blank=False)

    tags = models.ManyToManyField(Tag, related_name='photos')

    def __str__(self) -> str:
        return f"Photo({self.id}, {self.image.name})"
    