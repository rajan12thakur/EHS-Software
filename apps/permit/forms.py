from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import (
    Permit,
    PermitContractor,
    PermitAttachment,
    PermitExtension,
    PermitClosure,
)
from apps.organizations.models import Plant, Zone, Location, SubLocation


# ==============================================================================
# PERMIT FORM
# ==============================================================================

class PermitForm(forms.ModelForm):

    HAZARD_CHOICES = [
        ('fire', 'Fire'),
        ('gas', 'Gas'),
        ('fall', 'Fall'),
        ('electrical', 'Electrical'),
        ('chemical', 'Chemical'),
        ('noise', 'Noise'),
    ]

    hazards = forms.MultipleChoiceField(
        choices=HAZARD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Permit
        exclude = [
            'permit_number',
            'requester_user',
            'requester_name',
            'created_at',
            'updated_at',
            'status',
            'employees_count'
        ]

        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'job_description': forms.Textarea(attrs={'rows': 3}),
            'safety_measures': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 2}),
            'close_out_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ✅ Pre-fill hazards (IMPORTANT for edit)
        if self.instance and self.instance.pk and self.instance.hazards:
            self.initial['hazards'] = self.instance.hazards

        if user:
            self.fields['plant'].queryset = (
                user.assigned_plants.all()
                | (Plant.objects.filter(id=user.plant_id) if user.plant_id else Plant.objects.none())
            ).distinct()

        # Dynamic dropdowns
        if self.instance.pk:
            self.fields['zone'].queryset = Zone.objects.filter(plant=self.instance.plant)
            self.fields['location'].queryset = Location.objects.filter(zone=self.instance.zone)
            self.fields['sublocation'].queryset = SubLocation.objects.filter(location=self.instance.location)
        else:
            plant_id = self.data.get('plant')
            zone_id = self.data.get('zone')
            location_id = self.data.get('location')

            if plant_id:
                self.fields['zone'].queryset = Zone.objects.filter(plant_id=plant_id)

            if zone_id:
                self.fields['location'].queryset = Location.objects.filter(zone_id=zone_id)

            if location_id:
                self.fields['sublocation'].queryset = SubLocation.objects.filter(location_id=location_id)

    def clean_hazards(self):
        hazards = self.cleaned_data.get('hazards') 
        if not hazards:
            raise forms.ValidationError("Please select at least one hazard.")
        return hazards


class PermitExtensionRequestForm(forms.ModelForm):
    class Meta:
        model = PermitExtension
        fields = ['new_end_date', 'reason']
        widgets = {
            'new_end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'reason': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter reason for extension'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_end_date'].input_formats = ['%Y-%m-%dT%H:%M']


class PermitClosureForm(forms.ModelForm):
    class Meta:
        model = PermitClosure
        exclude = ['permit', 'closed_by', 'closed_at']
        widgets = {
            'actual_end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'work_status': forms.Select(attrs={'class': 'form-control'}),
            'work_summary': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'issues_encountered': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'closure_comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'contractor_signature': forms.HiddenInput(),
            'safety_signature': forms.HiddenInput(),
            'area_inspected': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
            'fire_watch_completed': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
            'equipment_isolated': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
            'hazards_removed': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
            'barriers_removed': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
            'no_incidents': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
            'area_clean': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
            'systems_operational': forms.CheckboxInput(attrs={'class': 'checklist-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        self.permit = kwargs.pop('permit', None)
        super().__init__(*args, **kwargs)
        self.fields['actual_end_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['work_status'].choices = [('', 'Select Status')] + list(self.fields['work_status'].choices)

    def clean(self):
        cleaned_data = super().clean()
        checklist_fields = [
            'area_inspected',
            'fire_watch_completed',
            'equipment_isolated',
            'hazards_removed',
            'barriers_removed',
            'no_incidents',
            'area_clean',
            'systems_operational',
        ]

        for field_name in checklist_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, "This checklist item must be confirmed before closing the permit.")

        if not cleaned_data.get('contractor_signature'):
            self.add_error('contractor_signature', "Contractor signature is required.")
        if not cleaned_data.get('safety_signature'):
            self.add_error('safety_signature', "Safety officer signature is required.")

        actual_end_date = cleaned_data.get('actual_end_date')
        if actual_end_date:
            if actual_end_date > timezone.now():
                self.add_error('actual_end_date', "Actual completion cannot be in the future.")
            if self.permit and self.permit.start_date and actual_end_date < self.permit.start_date:
                self.add_error('actual_end_date', "Actual completion cannot be before the permit start date.")

        return cleaned_data
    
# CONTRACTOR FORM
class PermitContractorForm(forms.ModelForm):
    class Meta:
        model = PermitContractor
        fields = ['name', 'trade', 'id_number', 'esi_number', 'contact_number']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Worker Name'}),
            'trade': forms.TextInput(attrs={'placeholder': 'Welder / Fitter'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False

# CONTRACTOR FORMSET
PermitContractorFormSet = inlineformset_factory(
    Permit,
    PermitContractor,
    form=PermitContractorForm,
    extra=1,
    can_delete=True,
    validate_min=False
)

# ATTACHMENT FORM
class PermitAttachmentForm(forms.ModelForm):
    class Meta:
        model = PermitAttachment
        fields = ['file', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['file'].required = False
        self.fields['description'].required = False

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get('file')
        description = cleaned_data.get('description')

        if not file and not description:
            self.cleaned_data = {}
            self._errors = {}
            return cleaned_data

        return cleaned_data
        
# ATTACHMENT FORMSET
PermitAttachmentFormSet = inlineformset_factory(
    Permit,
    PermitAttachment,
    form=PermitAttachmentForm,
    extra=1,
    can_delete=True
)
