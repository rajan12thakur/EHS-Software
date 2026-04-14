from django import forms
from django.forms import inlineformset_factory
from .models import (
    Permit,
    PermitContractor,
    PermitAttachment
)
from apps.organizations.models import Zone, Location, SubLocation


# ==============================================================================
# PERMIT FORM
# ==============================================================================

class PermitForm(forms.ModelForm):

    class Meta:
        model = Permit
        exclude = ['permit_number', 'requester_user', 'created_at', 'updated_at']

        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'job_description': forms.Textarea(attrs={'rows': 3}),
            'safety_measures': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 2}),
            'close_out_notes': forms.Textarea(attrs={'rows': 2}),
        }

    # -----------------------------
    # Dynamic cascading dropdowns
    # -----------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initially empty
        self.fields['zone'].queryset = Zone.objects.none()
        self.fields['location'].queryset = Location.objects.none()
        self.fields['sublocation'].queryset = SubLocation.objects.none()

        # Edit mode (instance exists)
        if self.instance and self.instance.pk:
            if self.instance.plant:
                self.fields['zone'].queryset = Zone.objects.filter(
                    plant=self.instance.plant
                )

            if self.instance.zone:
                self.fields['location'].queryset = Location.objects.filter(
                    zone=self.instance.zone
                )

            if self.instance.location:
                self.fields['sublocation'].queryset = SubLocation.objects.filter(
                    location=self.instance.location
                )

        # Create mode (POST data)
        else:
            if 'plant' in self.data:
                try:
                    plant_id = int(self.data.get('plant'))
                    self.fields['zone'].queryset = Zone.objects.filter(plant_id=plant_id)
                except:
                    pass

            if 'zone' in self.data:
                try:
                    zone_id = int(self.data.get('zone'))
                    self.fields['location'].queryset = Location.objects.filter(zone_id=zone_id)
                except:
                    pass

            if 'location' in self.data:
                try:
                    location_id = int(self.data.get('location'))
                    self.fields['sublocation'].queryset = SubLocation.objects.filter(location_id=location_id)
                except:
                    pass


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