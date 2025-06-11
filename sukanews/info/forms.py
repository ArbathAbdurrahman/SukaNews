from django import forms
from info.models import Info, Comment, Reply

class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['title', 'description', 'category', 'image', 'location', 'date', 'time_start', 'time_end', 'contact']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500',
                'required': True,
                'placeholder': 'Write a relevant title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 resize-vertical',
                'rows': 4,
                'required': True,
                'placeholder': 'Write a description to attract readers'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 cursor-pointer',
                'required': True,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'hidden',

            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500',
                'placeholder': 'Enter location address'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 cursor-pointer'
            }),
            'time_start': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 cursor-pointer'
            }),
            'time_end': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 cursor-pointer'
            }),
            'contact': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500',
                'placeholder': '08123456789'
            })
        }

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