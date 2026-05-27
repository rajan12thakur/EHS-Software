from django import forms

from .models import (
    ComplianceQuestion, LegalAct, ComplianceRequirement,)

from apps.organizations.models import (Plant, Department)

from django.contrib.auth import get_user_model

User = get_user_model()


class LegalActForm(forms.ModelForm):

    class Meta:
        model = LegalAct

        fields = [
            'act_name',
            'short_name',
            'authority_name',
            'government_level',
            'category',
            'description',
            'applicability_notes',
            'effective_date',
            'is_active',
        ]

        widgets = {
            'act_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Act Name'
            }),

            'short_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Short Name'
            }),

            'authority_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Authority Name'
            }),

            'government_level': forms.Select(attrs={
                'class': 'form-control'
            }),

            'category': forms.Select(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),

            'applicability_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),

            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class ComplianceRequirementForm(forms.ModelForm):

    class Meta:

        model = ComplianceRequirement

        fields = [

            # BASIC
            'title',
            'legal_act',
            'description',

            # CONFIGURATION
            'frequency',
            'criticality',
            'scheduled_date',
            'due_date',

            # WORKFLOW
            'evidence_required',
            'requires_approval',
            'due_days_before',
            'reminder_days',
            'escalation_days',

            # APPLICABILITY
            'applicable_plants',
            'applicable_departments',

            # RESPONSIBILITY
            'responsible_person',
            'reviewer',

            # STATUS
            'is_active',
        ]

        widgets = {

            # BASIC

            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Compliance Title'
            }),

            'legal_act': forms.Select(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter compliance description'
            }),

            # CONFIGURATION

            'frequency': forms.Select(attrs={
                'class': 'form-control'
            }),

            'criticality': forms.Select(attrs={
                'class': 'form-control'
            }),

            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            # WORKFLOW

            'evidence_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'requires_approval': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'due_days_before': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),

            'reminder_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),

            'escalation_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),

            # HIDDEN MULTISELECTS
            # UI is handled manually in template

            'applicable_plants': forms.SelectMultiple(attrs={
                'class': 'd-none'
            }),

            'applicable_departments': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'multiple': 'multiple'
            }),

            'responsible_person': forms.SelectMultiple(attrs={
                'class': 'd-none'
            }),

            'reviewer': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'multiple': 'multiple'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['legal_act'].queryset = (
            LegalAct.objects.filter(
                is_active=True
            ).order_by('act_name')
        )

        self.fields['applicable_plants'].queryset = (
            Plant.objects.filter(
                is_active=True
            ).order_by('name')
        )

        self.fields['applicable_departments'].queryset = (
            Department.objects.filter(
                is_active=True
            ).order_by('name')
        )

        self.fields['responsible_person'].queryset = (
            User.objects.filter(
                is_active=True
            ).order_by('first_name')
        )

        self.fields['reviewer'].queryset = (
            User.objects.filter(
                is_active=True
            ).order_by('first_name')
        )


class ComplianceQuestionFilterForm(forms.Form):

    legal_act = forms.ModelChoiceField(

        queryset=LegalAct.objects.filter(
            is_active=True
        ),

        required=False,

        empty_label='All Legal Acts',

        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    submission_type = forms.ChoiceField(

        choices=[
            ('', 'All Types')
        ] + ComplianceQuestion.SUBMISSION_TYPE_CHOICES,

        required=False,

        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    is_critical = forms.NullBooleanField(

        required=False,

        widget=forms.Select(

            choices=[

                ('', 'All Questions'),

                ('true', 'Critical Only'),

                ('false', 'Non-Critical')
            ],

            attrs={
                'class': 'form-control'
            }
        )
    )

    search = forms.CharField(

        required=False,

        widget=forms.TextInput(attrs={

            'class': 'form-control',

            'placeholder': 'Search questions...'
        })
    )



class ComplianceQuestionForm(forms.ModelForm):

    class Meta:

        model = ComplianceQuestion

        fields = [

            'legal_act',

            'question_text',

            'question_type',

            'submission_type',

            'is_mandatory',

            'is_document_required',

            'is_critical',

            'auto_generate_finding',

            'reference_standard',

            'guidance_notes',

            'applicable_plants',

            'applicable_departments',

            'is_active',
        ]

        widgets = {

            'legal_act': forms.Select(attrs={
                'class': 'form-control'
            }),

            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter compliance question'
            }),

            'question_type': forms.Select(attrs={
                'class': 'form-control'
            }),

            'submission_type': forms.Select(attrs={
                'class': 'form-control'
            }),

            'is_mandatory': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'is_document_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'is_critical': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'auto_generate_finding': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'reference_standard': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: OSHA 1910'
            }),

            'guidance_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional guidance'
            }),

            'applicable_plants': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'multiple': 'multiple'
            }),

            'applicable_departments': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'multiple': 'multiple'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['legal_act'].queryset = (

            LegalAct.objects.filter(
                is_active=True
            )

            .order_by('act_name')
        )

        self.fields['applicable_plants'].queryset = (

            Plant.objects.filter(
                is_active=True
            )

            .order_by('name')
        )

        self.fields['applicable_departments'].queryset = (

            Department.objects.filter(
                is_active=True
            )

            .order_by('name')
        )