from django import forms
from event.models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'image', 'location', 'date_start', 'date_end', 'time_start', 'time_end', 'guidebook', 'contact']
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
            'date_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 cursor-pointer'
            }),
            'date_end': forms.DateInput(attrs={
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
            'guidebook': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500',
                'placeholder': 'https://example.com/guidebook'
            }),
            'contact': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500',
                'placeholder': '08123456789'
            })
        }