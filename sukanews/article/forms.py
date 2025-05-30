from django import forms
from .models import Article, Comment, Reply
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=forms.HiddenInput())
    hashtags_input = forms.CharField(
        max_length=100,
        required=False,
        help_text="Add up to 5 hashtags, separated by spaces, e.g., #news #viral #trend",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 h-10 mt-2 bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors duration-200 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:text-white dark:border-gray-600',
            'placeholder': '#news #viral #trend'
        })
    )

    class Meta:
        model = Article
        fields = ['title', 'description', 'category', 'image', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-2 h-10 mt-2 bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors duration-200 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:text-white dark:border-gray-600',
                'required': True,
                'placeholder': 'Write a relevant title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 mt-2 bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors duration-200 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:text-white dark:border-gray-600',
                'rows': 4,
                'required': True,
                'placeholder': 'Write a description to attract readers'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-2 h-10 mt-2 bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors duration-200 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:text-white dark:border-gray-600',
                'required': True,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'absolute opacity-0 w-full h-full cursor-pointer',
                'id': 'customFileUpload',
                'multiple': False,
            }),
        }


    def clean_content(self):
        content = self.cleaned_data.get('content')
        # Remove HTML tags to count words
        plain_text = BeautifulSoup(content, "html.parser").get_text()
        word_count = len(plain_text.split())
        if word_count < 3:
            raise ValidationError('Content must be at least 300 words.')
        return content
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if self.instance and not self.instance.image:  # Jika instance ada tetapi gambar belum disimpan
            if not image:
                raise forms.ValidationError("Image is required.")
        return image
    
    def clean_hashtags_input(self):
        hashtags_input = self.cleaned_data.get('hashtags_input', '')
        hashtags = [tag.strip() for tag in hashtags_input.split() if tag.startswith('#')]

        # Validate number of hashtags
        if len(hashtags) > 5:
            raise forms.ValidationError("You can only add up to 5 hashtags.")
        
        # Validate individual hashtag length
        for tag in hashtags:
            if len(tag) > 50:
                raise forms.ValidationError(f"Hashtag '{tag}' is too long. Maximum length is 50 characters.")

        return hashtags

    def clean_title(self):
        title = self.cleaned_data.get('title')

        # Validate title length
        if len(title) < 20:
            raise forms.ValidationError("The title must be at least 20 characters long.")
        
        if len(title) > 100:
            raise forms.ValidationError("The title is too long. Maximum length is 100 characters.")

        return title

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:ring focus:ring-indigo-200',
                'placeholder': 'Write a comment...'
            })
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']