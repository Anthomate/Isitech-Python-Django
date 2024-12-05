from django import forms
from django.utils.translation import gettext_lazy as _
from .models import POST

class PostForm(forms.ModelForm):
    class Meta:
        model = POST
        fields = ['title', 'content', 'category', 'tags', 'image', 'status']
        labels = {
            'title': _('Title'),
            'content': _('Content'),
            'category': _('Category'),
            'tags': _('Tags'),
            'image': _('Image'),
            'status': _('Status'),
        }
        help_texts = {
            'title': _('Enter the title of your article.'),
            'content': _('Write the content of your article.'),
        }
