from django.db import models 
from modelcluster.fields import ParentalKey 
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.admin.panels import PageChooserPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)


class Product(Page): 
    sku = models.CharField(max_length=255) 
    short_description = models.TextField(blank=True, null=True) 
    price = models.DecimalField(decimal_places=2, max_digits=10) 
    image = models.ForeignKey( 
        'wagtailimages.Image', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='+' 
    ) 
    content_panels = Page.content_panels + [ 
        FieldPanel('sku'), 
        FieldPanel('price'), 
        PageChooserPanel('image'), 
        FieldPanel('short_description'), 
        InlinePanel('custom_fields', label='Custom fields'), 
    ]

class ProductCustomField(Orderable): 
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name='custom_fields') 
    name = models.CharField(max_length=255) 
    options = models.CharField(max_length=500, null=True, blank=True) 
    panels = [ 
        FieldPanel('name'), 
        FieldPanel('options') 
    ]

@register_setting 
class SnipcartSettings(BaseSiteSetting): 
    api_key = models.CharField( 
        max_length=255, 
        help_text='Your Snipcart public API key' 
    )