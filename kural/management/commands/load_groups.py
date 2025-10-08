from django.core.management.base import BaseCommand, no_translations
from django.contrib.auth.models import Group

GROUPS = ["admin", "student", "judge1", "judge2"]


class Command(BaseCommand):
    """
        This command loads the groups into table
        {
          name: "student",
          name: "judge",
          name: "admin"
        }
    """

    def handle(self, *args, **options):
        """
        """
        for group in GROUPS:
            group_obj, created = Group.objects.get_or_create(name=group)
            if created:
                group_obj.save()
