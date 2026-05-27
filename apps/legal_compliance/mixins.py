from apps.accounts.mixins import PermissionRequiredMixin


class LegalComplianceAccessMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'ACCESS_LEGAL_COMPLIANCE_MODULE'
    )


class LegalComplianceCreateMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'CREATE_LEGAL_COMPLIANCE'
    )


class LegalComplianceEditMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'EDIT_LEGAL_COMPLIANCE'
    )


class LegalComplianceViewMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'VIEW_LEGAL_COMPLIANCE'
    )


class LegalComplianceApproveMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'APPROVE_LEGAL_COMPLIANCE'
    )


class LegalComplianceCloseMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'CLOSE_LEGAL_COMPLIANCE'
    )


class LegalComplianceExportMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'EXPORT_LEGAL_COMPLIANCE'
    )


class LegalComplianceConfigMixin(
    PermissionRequiredMixin
):
    permission_required = (
        'MANAGE_LEGAL_COMPLIANCE_CONFIGURATION'
    )