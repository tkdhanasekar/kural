from django.core.management.base import BaseCommand, no_translations
from kural.models import MyUser
from django.contrib.auth.models import Group


class Command(BaseCommand):
    """
        This command assigns student role to users with Student
    """

    def handle(self, *args, **options):
        """
        """
        user_objs = MyUser.objects.filter(is_active=True,  is_admin=False)
        group, created = Group.objects.get_or_create(name='student')
        for user in user_objs:
            groups = [group.name for group in user.groups.all()]
            print(f"user: {user}, groups: {groups}")
            if 'admin' in groups or "judge1"  in groups or "judge2" in groups:
                print(f"Role Already exists for user: {user}, {groups}")
            else:
                if 'student' not in groups:
                    user.groups.add(group)
                    user.save()
                else:
                    print(f"Student Role Already exists for user: {user}, {groups}")
