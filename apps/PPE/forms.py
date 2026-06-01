from django import forms
from .models import PPEItem
from django.core.exceptions import ValidationError
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



class PPEItemForm(forms.ModelForm):

    class Meta:
        model = PPEItem
        fields = [
            'name',
            'category',
            'description',
            'manufacturer_brand',
            'model_number',
            'manufacturing_date',
            'expiry_date',
            'inspection_required',
            'replacement_required',
            'size_applicable',
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter PPE Name'
            }),

            'category': forms.Select(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description'
            }),

            'manufacturer_brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manufacturer / Brand'
            }),

            'model_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Model Number'
            }),

            'manufacturing_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'inspection_required': forms.Select(attrs={
                'class': 'form-control'
            }),

            'replacement_required': forms.Select(attrs={
                'class': 'form-control'
            }),

            'size_applicable': forms.Select(attrs={
                'class': 'form-control'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    # ---------------------------
    # VALIDATION LOGIC
    # ---------------------------

    def clean(self):
        cleaned_data = super().clean()

        mfg = cleaned_data.get('manufacturing_date')
        exp = cleaned_data.get('expiry_date')

        if mfg and exp:
            if exp <= mfg:
                raise ValidationError(
                    "Expiry date must be greater than Manufacturing date."
                )

        return cleaned_data