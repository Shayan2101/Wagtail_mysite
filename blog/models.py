from django import forms
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index   # Makes model searchable
from wagtail.snippets.models import register_snippet   # For reusable pieces of content which don’t exist as part of the page tree themselves
# from wagtailtrans.models import TranslatablePage   # To use multi-language


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    def get_context(self, request):
        '''
        Update context to include only published posts, ordered by reverse-chron
        '''
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context
    content_panels = Page.content_panels + [FieldPanel('intro')]

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage', 
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

class BlogTagIndexPage(Page):
    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)
        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField('blog.author', blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    def main_image(self):
        '''
        Returns the image from the first gallery item or None if no gallery items exist
        '''
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('authors', widget=forms.CheckboxSelectMultiple),   # The keyword widget used to specify a more user-friendly checkbox-based widget instead of the default multiple select boxes
            FieldPanel('tags'),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')   # Attaches the gallery images to a specific page
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(max_length=250, blank=True)
    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]

@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    panels = [
        FieldPanel('name'),
        FieldPanel('author_image'),
    ]
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Authors"

# class TransHomePage(TranslatablePage):
#     body = RichTextField(blank=True, default="")
#     content_panels = Page.content_panels + [
#         FieldPanel('body'),
#     ]

# class TranLandingPage(TranslatablePage):
#     body = RichTextField(blank=True, default="")
#     content_panels = Page.content_panels + [
#         FieldPanel('body'),
#     ]