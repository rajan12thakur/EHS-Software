from django import forms
from django.utils import timezone

from .models import Chemical, ChemicalRequest
from apps.organizations.models import Plant, Zone, Location, SubLocation, Department


class ChemicalForm(forms.ModelForm):
    receipt_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    expiration_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    GHS_CHOICES = [
        ('flammable', 'Flammable'),
        ('corrosive', 'Corrosive'),
        ('health_hazard', 'Health Hazard'),
        ('acute_toxic', 'Acutely Toxic'),
    ]

    PPE_CHOICES = [
        ('goggles', 'Safety Goggles'),
        ('gloves', 'Nitrile Gloves'),
        ('lab_coat', 'Lab Coat'),
    ]

    ehs_ghs = forms.MultipleChoiceField(
        choices=GHS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    ehs_ppe = forms.MultipleChoiceField(
        choices=PPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Chemical
        exclude = ['created_by', 'created_at']
        widgets = {
            'ehs_compliance': forms.HiddenInput(),  # hide raw JSON
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Location
        self.fields['plant'].queryset = Plant.objects.filter(is_active=True).order_by('name')
        self.fields['zone'].queryset = Zone.objects.none()
        self.fields['location'].queryset = Location.objects.none()
        self.fields['sublocation'].queryset = SubLocation.objects.none()
        self.fields['department'].queryset = Department.objects.order_by('name')

        if self.data.get('plant'):
            try:
                plant_id = int(self.data['plant'])
                self.fields['zone'].queryset = Zone.objects.filter(plant_id=plant_id, is_active=True).order_by('name')
            except:
                pass

        if self.data.get('zone'):
            try:
                zone_id = int(self.data['zone'])
                self.fields['location'].queryset = Location.objects.filter(zone_id=zone_id, is_active=True).order_by('name')
            except:
                pass

        if self.data.get('location'):
            try:
                location_id = int(self.data['location'])
                self.fields['sublocation'].queryset = SubLocation.objects.filter(location_id=location_id, is_active=True).order_by('name')
            except:
                pass

        # LOAD EXISTING JSON 
        if self.instance and self.instance.ehs_compliance:
            self.fields['ehs_ghs'].initial = self.instance.ehs_compliance.get('ghs', [])
            self.fields['ehs_ppe'].initial = self.instance.ehs_compliance.get('ppe', [])

    def clean(self):
        cleaned_data = super().clean()

        plant = cleaned_data.get('plant')
        zone = cleaned_data.get('zone')
        location = cleaned_data.get('location')
        sublocation = cleaned_data.get('sublocation')

        if zone and plant and zone.plant != plant:
            self.add_error('zone', "Zone does not belong to the selected Plant.")

        if location and zone and location.zone != zone:
            self.add_error('location', "Location does not belong to the selected Zone.")

        if sublocation and location and sublocation.location != location:
            self.add_error('sublocation', "SubLocation does not belong to the selected Location.")

        return cleaned_data

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get('expiration_date')
        receipt_date = self.cleaned_data.get('receipt_date')

        if expiration_date and receipt_date and expiration_date <= receipt_date:
            raise forms.ValidationError("Expiration date must be after the receipt date.")

        return expiration_date

    def clean_cas_number(self):
        cas_number = self.cleaned_data.get('cas_number')
        if cas_number:
            import re
            if not re.match(r'^\d{2,7}-\d{2}-\d$', cas_number):
                raise forms.ValidationError(
                    "Enter a valid CAS number in the format XXXXXXX-XX-X."
                )
        return cas_number

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    # Json Fields
    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.ehs_compliance = {
            "ghs": self.cleaned_data.get('ehs_ghs', []),
            "ppe": self.cleaned_data.get('ehs_ppe', []),
        }

        if commit:
            instance.save()

        return instance


class ChemicalRequestForm(forms.ModelForm):

    class Meta:
        model = ChemicalRequest
        exclude = [
            'requester_user',
            'requester_name',
            'status',
            'approved_by',
            'approved_at',
            'rejection_reason',
            'chemical',
            'created_at',
        ]
        widgets = {
            'justification': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide a justification for this request...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['plant'].queryset = Plant.objects.filter(is_active=True).order_by('name')
        self.fields['zone'].queryset = Zone.objects.none()
        self.fields['location'].queryset = Location.objects.none()
        self.fields['sublocation'].queryset = SubLocation.objects.none()
        self.fields['department'].queryset = Department.objects.order_by('name')

        if self.data.get('plant'):
            try:
                plant_id = int(self.data['plant'])
                self.fields['zone'].queryset = Zone.objects.filter(plant_id=plant_id, is_active=True).order_by('name')
            except (ValueError, TypeError):
                pass

        if self.data.get('zone'):
            try:
                zone_id = int(self.data['zone'])
                self.fields['location'].queryset = Location.objects.filter(zone_id=zone_id, is_active=True).order_by('name')
            except (ValueError, TypeError):
                pass

        if self.data.get('location'):
            try:
                location_id = int(self.data['location'])
                self.fields['sublocation'].queryset = SubLocation.objects.filter(location_id=location_id, is_active=True).order_by('name')
            except (ValueError, TypeError):
                pass

        if self.instance and self.instance.pk:
            if self.instance.plant:
                self.fields['zone'].queryset = Zone.objects.filter(plant=self.instance.plant, is_active=True).order_by('name')
            if self.instance.zone:
                self.fields['location'].queryset = Location.objects.filter(zone=self.instance.zone, is_active=True).order_by('name')
            if self.instance.location:
                self.fields['sublocation'].queryset = SubLocation.objects.filter(location=self.instance.location, is_active=True).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        plant = cleaned_data.get('plant')
        zone = cleaned_data.get('zone')
        location = cleaned_data.get('location')
        sublocation = cleaned_data.get('sublocation')

        if zone and plant and zone.plant != plant:
            self.add_error('zone', "Zone does not belong to the selected Plant.")

        if location and zone and location.zone != zone:
            self.add_error('location', "Location does not belong to the selected Zone.")

        if sublocation and location and sublocation.location != location:
            self.add_error('sublocation', "SubLocation does not belong to the selected Location.")

        return cleaned_data

    def clean_cas_number(self):
        cas_number = self.cleaned_data.get('cas_number')
        if cas_number:
            import re
            if not re.match(r'^\d{2,7}-\d{2}-\d$', cas_number):
                raise forms.ValidationError(
                    "Enter a valid CAS number in the format XXXXXXX-XX-X."
                )
        return cas_number

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.requester_user = self.user
            if not instance.requester_name:
                instance.requester_name = (
                    self.user.get_full_name() or self.user.username
                )
        if commit:
            instance.save()
        return instance


class ChemicalRequestApprovalForm(forms.ModelForm):
    """
    Used by EHS managers / approvers to approve or reject a ChemicalRequest.
    """

    class Meta:
        model = ChemicalRequest
        fields = ['status', 'rejection_reason', 'chemical']
        widgets = {
            'rejection_reason': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Required if rejecting the request...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.approver = kwargs.pop('approver', None)
        super().__init__(*args, **kwargs)

        # Only allow terminal status transitions
        self.fields['status'].choices = [
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ]
        self.fields['chemical'].required = False
        self.fields['rejection_reason'].required = False

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'rejected' and not rejection_reason:
            self.add_error('rejection_reason', "A rejection reason is required when rejecting a request.")

        if status == 'approved' and not cleaned_data.get('chemical'):
            # Warn but don't block — chemical may be added to inventory later
            pass

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.approver:
            instance.approved_by = self.approver
        instance.approved_at = timezone.now()
        if commit:
            instance.save()
        return instance
