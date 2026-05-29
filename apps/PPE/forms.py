from django import forms
from apps.accounts.models import User
from apps.organizations.models import Plant, Zone, Location, SubLocation, Department
from django.core.exceptions import ValidationError
from .models import (
    PPECategory
)

class PPECategoryForm(forms.ModelForm):
    class Meta:
        model = PPECategory
        fields = [
            'category_name',
            'category_code',
            'description',
            'is_active'
        ]
        widgets = {
            'category_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name (e.g., Head Protection,Eye Protection)'
            }),
            'category_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., HP,EP,FP',
                'maxlength': '12'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description of this category'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    def clean_categorycode(self):
        code = self.cleaned_data.get('category_code')
        if code:
            code = code.upper()
            existing = PPECategory.objects.filter(category_code=code)
            if self.instance.pk:
                existing= existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(f'Category Code "{code}" already exist.')
        return code

