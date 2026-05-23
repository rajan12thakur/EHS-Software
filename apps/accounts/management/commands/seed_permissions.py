from django.core.management.base import BaseCommand
from apps.accounts.models import Permissions

class Command(BaseCommand):
    help = 'Seeds Permission Master with hierarchical structure'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting permission seed...'))
        
        permissions_data = [
            # (code, name, description, module, permission_type, display_order)

            # Dashboards
            ('ACCESS_DASHBOARD', 'Access Dashboard', 'Can access dashboards',
            'DASHBOARD', 'MODULE_ACCESS', 0),

            ('INJURY_DASHBOARD', 'Access Injury Dashboard',
            'Can access Injury dashboard',
            'DASHBOARD', 'VIEW', 1),

            ('HAZARD_DASHBOARD', 'Access Hazard Dashboard',
            'Can access Hazard dashboard',
            'DASHBOARD', 'VIEW', 2),

            ('INSPECTION_DASHBOARD', 'Access Inspection Dashboard',
            'Can access Inspection dashboard',
            'DASHBOARD', 'VIEW', 3),
            # === USER MANAGEMENT ===
            ('CAN_CREATE_USERS', 'Can Create Users', 'Can create users for their assigned plants only',
            None, 'MANAGE', 0),
            # === Organization Setup ===
            ('CAN_ACCESS_ORGANIZATION', 'Access Organization Setup', 'Can Access Organization Setup',None,'MANAGE',0),
            # === INJURY MODULE ===
            ('ACCESS_INJURY_MODULE', 'Access Injury Module', 'Can access injury module', 
             'INJURY', 'MODULE_ACCESS', 0),
            ('CREATE_INJURY', 'Create Injury', 'Can create injuries', 
             'INJURY', 'CREATE', 1),
            ('EDIT_INJURY', 'Edit Injury', 'Can edit injuries', 
             'INJURY', 'EDIT', 2),
            ('VIEW_INJURY', 'View Injury', 'Can view injuries', 
             'INJURY', 'VIEW', 3),
            # ('DELETE_INJURY', 'Delete Injury', 'Can delete injuries', 
            #  'INJURY', 'DELETE', 4),
            ('INVESTIGATE_INJURY', 'Investigate Injury', 'Can investigate injuries', 
             'INJURY', 'MANAGE', 4),
            ('ADD_INJURY_ACTION', 'Add Injury Action', 'Can add action items', 
             'INJURY', 'MANAGE', 5),
            ('APPROVE_INJURY', 'Approve Injury', 'Can approve injuries', 
             'INJURY', 'APPROVE', 6),
            ('CLOSE_INJURY', 'Close Injury', 'Can close injuries', 
             'INJURY', 'CLOSE', 7),
            ('EXPORT_INJURY_PDF','Export Injury PDF','Can export injuries pdf',
            'INJURY','EXPORT',8),
            
            # === HAZARD MODULE ===
            ('ACCESS_HAZARD_MODULE', 'Access Hazard Module', 'Can access hazard module', 
             'HAZARD', 'MODULE_ACCESS', 0),
            ('CREATE_HAZARD', 'Create Hazard', 'Can create hazards', 
             'HAZARD', 'CREATE', 1),
            ('EDIT_HAZARD', 'Edit Hazard', 'Can edit hazards', 
             'HAZARD', 'EDIT', 2),
            ('VIEW_HAZARD', 'View Hazard', 'Can view hazards', 
             'HAZARD', 'VIEW', 3),
            # ('DELETE_HAZARD', 'Delete Hazard', 'Can delete hazards', 
            #  'HAZARD', 'DELETE', 4),
            ('ADD_HAZARD_ACTION', 'Add Hazard Action', 'Can add action items', 
             'HAZARD', 'MANAGE', 4),
            ('EDIT_HAZARD_ACTION', 'Edit Hazard Action', 'Can edit action items', 
             'HAZARD', 'MANAGE', 5),
            ('EXPORT_HAZARD_PDF','Export Hazard PDF','Can export hazards pdf',
            'HAZARD','EXPORT',6),
            # ('DELETE_HAZARD_ACTION', 'Delete Hazard Action', 'Can delete action items', 
            #  'HAZARD', 'MANAGE', 6),
            # ('APPROVE_HAZARD', 'Approve Hazard', 'Can approve hazards', 
            #  'HAZARD', 'APPROVE', 7),
            # ('CLOSE_HAZARD', 'Close Hazard', 'Can close hazards', 
            #  'HAZARD', 'CLOSE', 8),
            
            # === INSPECTION MODULE ===
            ('ACCESS_INSPECTION_MODULE', 'Access Inspection Module', 'Can access inspection module', 
             'INSPECTION', 'MODULE_ACCESS', 0),
            ('CREATE_INSPECTION', 'Create Inspection', 'Can create inspections', 
             'INSPECTION', 'CREATE', 1),
            ('CONDUCT_INSPECTION', 'Conduct Inspection', 'Can conduct inspections', 
             'INSPECTION', 'MANAGE', 2),
            ('VIEW_INSPECTION', 'View Inspection', 'Can view inspections', 
             'INSPECTION', 'VIEW', 3),
            # ('APPROVE_INSPECTION', 'Approve Inspection', 'Can approve inspections', 
            #  'INSPECTION', 'APPROVE', 4),
            ('VIEW_NO_ANSWER_ITEMS', 'View No Answer Items', 'Can view no answer assigned items',
            'INSPECTION', 'VIEW', 4),
            ('MANAGE_INSPECTION_CONFIGURATION', 'Manage Inspection Configuration', 'Can manage inspection configuration',
            'INSPECTION', 'MANAGE', 5),
            # === REPORTS MODULE ===
            # ('ACCESS_REPORTS_MODULE', 'Access Reports Module', 'Can access reports module', 
            #  'REPORTS', 'MODULE_ACCESS', 0),
            # ('GENERATE_REPORTS', 'Generate Reports', 'Can generate reports', 
            #  'REPORTS', 'MANAGE', 1),
            # ('VIEW_REPORTS', 'View Reports', 'Can view reports', 
            #  'REPORTS', 'VIEW', 2),
            # ('EXPORT_REPORTS', 'Export Reports', 'Can export reports', 
            #  'REPORTS', 'EXPORT', 3),
            
            # === ENV DATA MODULE ===
            ('ACCESS_ENV_DATA_MODULE', 'Access Env Data Module', 'Can access environmental data module', 
             'ENV_DATA', 'MODULE_ACCESS', 0),
            ('CREATE_ENV_DATA', 'Enter Env Data', 'Can enter environmental data', 
             'ENV_DATA', 'CREATE', 1),
            # ('EDIT_ENV_DATA', 'Edit Env Data', 'Can edit environmental data', 
            #  'ENV_DATA', 'EDIT', 2),
            ('VIEW_ENV_DATA', 'View Env Data', 'Can view environmental data', 
             'ENV_DATA', 'VIEW', 2),
            # ('DELETE_ENV_DATA', 'Delete Env Data', 'Can delete environmental data', 
            #  'ENV_DATA', 'DELETE', 4),
            # ('MANAGE_ENV_QUESTIONS', 'Manage Env Questions', 'Can manage questions', 
            #  'ENV_DATA', 'MANAGE', 4),
            # ('MANAGE_ENV_UNITS', 'Manage Units', 'Can manage units', 
            #  'ENV_DATA', 'MANAGE', 5),
            ('EXPORT_ENV_DATA', 'Export Env Data', 'Can export data', 
             'ENV_DATA', 'EXPORT', 3),

            # === EMERGENCY MODULE ===
            ('ACCESS_EMERGENCY_MODULE', 'Access Emergency Module', 'Can access emergency module',
             'EMERGENCY', 'MODULE_ACCESS', 0),
            ('CREATE_EMERGENCY_REPORT', 'Create Emergency Report', 'Can create emergency reports',
             'EMERGENCY', 'CREATE', 1),
            ('VIEW_EMERGENCY_REPORT', 'View Emergency Report', 'Can view emergency reports',
             'EMERGENCY', 'VIEW', 2),

            # === TRAINING MODULE ===
            ('ACCESS_TRAINING_MODULE', 'Access Training Module', 'Can access training module',
            'TRAINING', 'MODULE_ACCESS', 0),

            ('CREATE_TRAINING_SESSION', 'Create Training Session', 'Can create training sessions',
            'TRAINING', 'CREATE', 1),

            ('EDIT_TRAINING_SESSION', 'Edit Training Session', 'Can edit training sessions',
            'TRAINING', 'EDIT', 2),

            ('VIEW_TRAINING_SESSION', 'View Training Session', 'Can view training sessions',
            'TRAINING', 'VIEW', 3),

            ('MARK_TRAINING_ATTENDANCE', 'Mark Training Attendance', 'Can mark attendance for sessions',
            'TRAINING', 'MANAGE', 4),

            ('UPLOAD_TRAINING_CERTIFICATE', 'Upload Training Certificate', 'Can upload certificates manually',
            'TRAINING', 'MANAGE', 5),

            ('VIEW_TRAINING_COMPLIANCE', 'View Training Compliance', 'Can view compliance matrix/reports',
            'TRAINING', 'VIEW', 6),

            ('MANAGE_TRAINING_TOPICS', 'Manage Training Topics', 'Can create/edit training topics master',
            'TRAINING', 'MANAGE', 7),

            ('MANAGE_TRAINING_REQUIREMENTS', 'Manage Training Requirements', 'Can define who needs what training',
            'TRAINING', 'MANAGE', 8),

            ('CLOSE_TRAINING_SESSION', 'Close Training Session', 'Can mark session as completed',
            'TRAINING', 'CLOSE', 9),

            # === PERMIT DATA MODULE ===
            ('ACCESS_PERMIT_MODULE', 'Access Permit Module', 'Can access permit module', 
             'PERMIT', 'MODULE_ACCESS', 0),
            ('CREATE_PERMIT', 'Create Permit', 'Can create permit', 
             'PERMIT', 'CREATE', 1),
            ('VIEW_PERMIT', 'View Permit', 'Can view permit', 
             'PERMIT', 'VIEW', 2),
            ('APPROVE_PERMIT', 'Approve Permit', 'Can approve permit', 
             'PERMIT', 'APPROVE', 3),
            ('MANAGE_PERMIT_CONFIGURATION', 'Manage Permit Configuration', 'Can manage permit configuration',
            'PERMIT', 'MANAGE', 4),

            # === CHEMICAL DATA MODULE ===
            ('ACCESS_CHEMICAL_MODULE', 'Access Chemical Module', 'Can access chemical module', 
             'CHEMICAL', 'MODULE_ACCESS', 0),
            ('ADD_CHEMICAL', 'Add Chemical', 'Can add chemical', 
             'CHEMICAL', 'CREATE', 1),
            ('REQUEST_CHEMICAL', 'Request Chemical', 'Can request chemical', 
             'CHEMICAL', 'CREATE', 2),
            ('VIEW_CHEMICAL', 'View Chemical', 'Can view chemical', 
             'CHEMICAL', 'VIEW', 3),
            ('APPROVE_CHEMICAL', 'Approve Chemical', 'Can approve chemical', 
             'CHEMICAL', 'APPROVE', 4),

            # === AUDIT DATA MODULE ===
            ('ACCESS_AUDIT_MODULE', 'Access Audit Module', 'Can access audit module', 
             'AUDIT', 'MODULE_ACCESS', 0),
            ('CREATE_AUDIT', 'Create Audit', 'Can create audit', 
             'AUDIT', 'CREATE', 1),
            ('CONDUCT_AUDIT', 'Conduct Audit', 'Can conduct audit', 
             'AUDIT', 'CREATE', 2),
            ('VIEW_AUDIT', 'View Audit', 'Can view audit', 
             'AUDIT', 'VIEW', 3),
             ('VIEW_OPEN_FINDINGS', 'View Open Findings', 'Can view open findings',
            'AUDIT', 'VIEW', 4),
            ('APPROVE_FINDING', 'Approve Finding', 'Can approve finding', 
             'AUDIT', 'APPROVE', 5),
            ('CREATE_CAPA', 'Create CAPA', 'Can create CAPA', 
             'AUDIT', 'CREATE', 6),
            ('MANAGE_AUDIT_CONFIGURATION', 'Manage Audit Configuration', 'Can manage audit configuration',
            'AUDIT', 'MANAGE', 7),
        ]

        created = 0
        updated = 0
        
        for code, name, desc, module, perm_type, order in permissions_data:
            perm, is_created = Permissions.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'module': module,
                    'permission_type': perm_type,
                    'display_order': order
                }
            )
            if is_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {code}'))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f'⟳ Updated: {code}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created: {created}'))
        self.stdout.write(self.style.WARNING(f'⟳ Updated: {updated}'))
        self.stdout.write(self.style.SUCCESS(f'━ Total: {created + updated}\n'))
