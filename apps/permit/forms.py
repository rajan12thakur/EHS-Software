from django import forms
from django.forms import inlineformset_factory
from .models import (
    Permit,
    PermitContractor,
    PermitAttachment
)
from apps.organizations.models import Plant, Zone, Location, SubLocation


# ==============================================================================
# PERMIT FORM
# ==============================================================================

class PermitForm(forms.ModelForm):

    hazards = forms.MultipleChoiceField(
        choices=[
            ('fire', 'Fire'),
            ('gas', 'Gas'),
            ('fall', 'Fall'),
            ('electrical', 'Electrical'),
            ('chemical', 'Chemical'),
            ('noise', 'Noise'),
        ],
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

        if user:
            self.fields['plant'].queryset = (
                user.assigned_plants.all()
                | (Plant.objects.filter(id=user.plant_id) if user.plant_id else Plant.objects.none())
            ).distinct()

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
        return self.cleaned_data.get('hazards', [])
    
# CONTRACTOR FORM
class PermitContractorForm(forms.ModelForm):
    class Meta:
        model = PermitContractor
        fields = ['name', 'trade', 'id_number', 'esi_number', 'contact_number']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Worker Name'}),
            'trade': forms.TextInput(attrs={'placeholder': 'Welder / Fitter'}),
        }


# CONTRACTOR FORMSET
PermitContractorFormSet = inlineformset_factory(
    Permit,
    PermitContractor,
    form=PermitContractorForm,
    extra=1,
    can_delete=True
)

# ATTACHMENT FORM
class PermitAttachmentForm(forms.ModelForm):
    class Meta:
        model = PermitAttachment
        fields = ['file', 'description']

        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'File description'}),
        }


# ATTACHMENT FORMSET
PermitAttachmentFormSet = inlineformset_factory(
    Permit,
    PermitAttachment,
    form=PermitAttachmentForm,
    extra=1,
    can_delete=True
)