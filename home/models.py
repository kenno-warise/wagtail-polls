from django.db import models  # type:ignore

from wagtail.models import Page  # type:ignore
from wagtail.fields import RichTextField  # type:ignore
from wagtail.admin.panels import FieldPanel  # type:ignore


class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
            FieldPanel('body'),
    ]

