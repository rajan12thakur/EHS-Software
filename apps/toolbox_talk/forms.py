from django import forms

from .models import ToolboxTalkCategory


class ToolboxTalkCategoryForm(forms.ModelForm):

    class Meta:

        model = ToolboxTalkCategory

        fields = [
            'category_name',
            'short_code',
            'description',
            'is_active'
        ]

        widgets = {

            'category_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),

            'short_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter short code'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })

        }