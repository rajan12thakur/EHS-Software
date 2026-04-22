from django import forms
from django.forms import formset_factory, modelformset_factory
from django.db.models import Q
from apps.accounts.models import User
from apps.organizations.models import Location, Plant, Zone, SubLocation

from .models import AuditCategory, AuditFinding, AuditQuestion, AuditResponse, AuditSchedule, AuditTemplate, CAPA


class AuditCategoryForm(forms.ModelForm):
    class Meta:
        model = AuditCategory
        fields = ["category_name", "category_code", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class AuditTemplateForm(forms.ModelForm):
    class Meta:
        model = AuditTemplate
        fields = ["title", "version", "category", "standard_reference"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = AuditCategory.objects.filter(is_active=True).order_by("category_name")


class AuditScheduleForm(forms.ModelForm):
    plants = forms.ModelMultipleChoiceField(
        queryset=Plant.objects.filter(is_active=True),
        required=True,
        widget=forms.MultipleHiddenInput(),
    )
    zones = forms.ModelMultipleChoiceField(
        queryset=Zone.objects.filter(is_active=True),
        required=False,
        widget=forms.MultipleHiddenInput(),
    )
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        widget=forms.MultipleHiddenInput(),
    )
    sublocations = forms.ModelMultipleChoiceField(
        queryset=SubLocation.objects.filter(is_active=True),
        required=False,
        widget=forms.MultipleHiddenInput(),
    )

    class Meta:
        model = AuditSchedule
        fields = ["template", "auditor", "location", "scheduled_date", "priority"]
        widgets = {
            "template": forms.Select(attrs={"class": "form-control"}),
            "auditor": forms.Select(attrs={"class": "form-control"}),
            "scheduled_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["auditor"].queryset = User.objects.filter(
            Q(role__permissions__code="CONDUCT_AUDIT"),is_active=True
        ).exclude(Q(is_superuser=True) | Q(role__name='ADMIN')).distinct()
        self.fields["location"].required = False
        self.fields["location"].widget = forms.HiddenInput()
        if self.instance.pk:
            self.fields["plants"].initial = self.instance.plants.all()
            self.fields["zones"].initial = self.instance.zones.all()
            self.fields["locations"].initial = self.instance.locations.all()
            self.fields["sublocations"].initial = self.instance.sublocations.all()

    def save(self, commit=True):
        schedule = super().save(commit=False)
        selected_locations = list(self.cleaned_data.get("locations", []))
        if selected_locations:
            schedule.location = selected_locations[0]
        elif self.cleaned_data.get("sublocations"):
            schedule.location = self.cleaned_data["sublocations"][0].location

        if commit:
            schedule.save()
            self.save_related_locations(schedule)
        else:
            self._pending_location_relations = {
                "plants": self.cleaned_data.get("plants"),
                "zones": self.cleaned_data.get("zones"),
                "locations": self.cleaned_data.get("locations"),
                "sublocations": self.cleaned_data.get("sublocations"),
            }
        return schedule

    def save_related_locations(self, schedule):
        schedule.plants.set(self.cleaned_data.get("plants"))
        schedule.zones.set(self.cleaned_data.get("zones"))
        schedule.locations.set(self.cleaned_data.get("locations"))
        schedule.sublocations.set(self.cleaned_data.get("sublocations"))


class AuditQuestionForm(forms.ModelForm):
    class Meta:
        model = AuditQuestion
        fields = ["question_text", "compliance_clause", "is_mandatory_photo", "sequence"]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 3}),
            "compliance_clause": forms.TextInput(attrs={"placeholder": "e.g. ISO 45001 - 8.1.2"}),
        }


AuditQuestionFormSet = modelformset_factory(
    AuditQuestion,
    form=AuditQuestionForm,
    extra=5,
    can_delete=False,
)


class AuditExecutionLineForm(forms.Form):
    response_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    question_id = forms.IntegerField(widget=forms.HiddenInput())
    previous_status = forms.CharField(widget=forms.HiddenInput(), required=False)
    status = forms.ChoiceField(choices=[("", "Select"), *AuditResponse.STATUS_CHOICES], required=True)
    comment = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
    photo_evidence = forms.ImageField(required=False)
    observation_detail = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
    risk_score = forms.ChoiceField(choices=AuditFinding.RISK_CHOICES, required=False)
    archive_finding = forms.BooleanField(required=False)


AuditExecutionFormSet = formset_factory(AuditExecutionLineForm, extra=0)


class AuditFindingReviewForm(forms.ModelForm):
    decision = forms.ChoiceField(
        choices=[
            (AuditFinding.REVIEW_APPROVED, "Approve"),
            (AuditFinding.REVIEW_REJECTED, "Reject"),
        ]
    )

    class Meta:
        model = AuditFinding
        fields = ["decision", "manager_review_comment", "risk_score"]
        widgets = {
            "manager_review_comment": forms.Textarea(attrs={"rows": 3}),
        }


class CAPACreateForm(forms.ModelForm):
    class Meta:
        model = CAPA
        fields = ["action_required", "assigned_to", "due_date"]
        widgets = {
            "action_required": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(is_active=True).exclude(Q(is_superuser=True) | Q(role__name='ADMIN')).order_by("first_name", "username")

class CAPAUpdateForm(forms.ModelForm):
    mark_as_fixed = forms.BooleanField(required=False)

    class Meta:
        model = CAPA
        fields = ["evidence_of_fix", "fixed_comment", "verification_status"]
        widgets = {
            "fixed_comment": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("mark_as_fixed"):
            cleaned_data["verification_status"] = CAPA.STATUS_FIXED
        return cleaned_data
