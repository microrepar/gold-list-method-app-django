import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Populates auth_group, auth_permission, and auth_group_permissions tables with data from JSON files.'

    def handle(self, *args, **options):
        # Define the path to the JSON files
        base_dir = Path(settings.BASE_DIR)
        groups_file = base_dir / '.groups_permissions_data' / 'auth_group.json'
        permissions_file = base_dir / '.groups_permissions_data' / 'auth_permission.json'
        group_permissions_file = base_dir / '.groups_permissions_data' / 'auth_group_permissions.json'
        
        # Load the group data from the JSON file
        with open(groups_file, 'r') as f:
            groups_data = json.load(f)['auth_group']
        
        # Load the permission data from the JSON file
        with open(permissions_file, 'r') as f:
            permissions_data = json.load(f)['auth_permission']
        
        # Load the group_permissions data from the JSON file
        with open(group_permissions_file, 'r') as f:
            group_permissions_data = json.load(f)['auth_group_permissions']
        
        # Clear existing data
        Group.objects.all().delete()
        Permission.objects.all().delete()
        
        # Create groups with specified IDs
        for group_data in groups_data:
            Group.objects.update_or_create(
                id=group_data['id'],
                defaults={'name': group_data['name']}
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated auth_group table.'))
        
        # Create permissions with specified IDs
        for perm_data in permissions_data:
            Permission.objects.update_or_create(
                id=perm_data['id'],
                defaults={
                    'name': perm_data['name'],
                    'codename': perm_data['codename'],
                    'content_type': ContentType.objects.get(id=perm_data['content_type_id'])
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated auth_permission table.'))

        
        # Create group_permissions with specified IDs
        for gp_data in group_permissions_data:
            group = Group.objects.get(id=gp_data['group_id'])
            permission = Permission.objects.get(id=gp_data['permission_id'])
            group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS('Successfully populated tables with data from JSON files.'))
