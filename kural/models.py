from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import PermissionsMixin


# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, *args, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not kwargs.get('student_id') or kwargs.get('family_id'):
            raise ValueError('Users must have an family id and student id')

        user = self.model(
            student_id=self.normalize_email(kwargs.get('student_id')),
            student_full_name=kwargs.get('full_name'),
            class_levels=kwargs.get('class_levels'),
            is_active=kwargs.get('is_active', True),
            date_of_birth=kwargs.get('date_of_birth', ''),
        )

        #
        group_name = kwargs.get('group', None)
        if not group_name:
            group_name = 'student'
        group = Group.objects.filter(name=group_name)
        if group.exists():
            user.groups.add(group.first())

        user.set_password(kwargs.get('password'))
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kwargs):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.model(
            student_id=self.normalize_email(kwargs.get('student_id')),
            student_full_name=kwargs.get('student_full_name'),
            class_levels=kwargs.get('class_levels'),
            is_active=kwargs.get('is_active', True),
            date_of_birth=kwargs.get('date_of_birth', 'NA'),
        )

        user.set_password(kwargs.get('password'))
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    student_id = models.CharField(
        verbose_name='student_id',
        max_length=255,
        unique=True,
    )
    family_id = models.CharField(
        verbose_name='family_id',
        max_length=255,
        null=False,
        blank=False
    )
    student_full_name = models.CharField(max_length=1024, null=False, blank=False)
    class_levels = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.CharField(max_length=100, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['student_full_name', 'family_id']

    def __str__(self):
        return self.student_full_name

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always

        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Tirukkural(models.Model):
    """
        This schema stores tirukural data
    """
    kural_id = models.IntegerField(db_index=True, unique=True)
    line_1 = models.CharField(max_length=1024, null=False, blank=False)
    line_2 = models.CharField(max_length=1024, null=False, blank=False)
    translation = models.TextField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    transliteration1 = models.CharField(max_length=1024, null=False, blank=False)
    transliteration2 = models.CharField(max_length=1024, null=False, blank=False)
    author_by = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    munnurai = models.CharField(max_length=2048, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)


class UserKurals(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    kural_ids = models.TextField(null=False)
    pdf_path = models.CharField(max_length=1024, null=True, blank=True)
    year = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)


class Cutoffdate(models.Model):
    event_name = models.CharField(max_length=255, null=True, blank=True)
    event_cutoff_date = models.DateField(null=False)
    event_year = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)


class Students(models.Model):
    student_id = models.CharField(max_length=255, unique=True, blank=False, null=False)
    family_id = models.CharField(max_length=255, null=False, blank=False)
    student_full_name = models.CharField(max_length=1024, null=False, blank=False)
    class_levels = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)


class KuralMarks(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    judge = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='judge')
    kural_id = models.IntegerField(null=False)
    tirukkural = models.TextField(null=True)
    munnurai = models.TextField(null=True)
    judge_kural_marks = models.FloatField(default=0.0)
    judge_porul_marks = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)


class StudentCompetition(models.Model):
    class_levels = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('class_levels', 'name',)


class CompetitionDate(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    event1_date = models.DateField(null=True, blank=True)
    event2_date = models.DateField(null=True, blank=True)
    cutoff_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'event1_date', 'event2_date')


class Registration(models.Model):
    competition_id = models.IntegerField(null=False, blank=False)
    student = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    class_levels = models.CharField(max_length=255, null=False, blank=False)
    is_kural_interested = models.BooleanField(default=True)
    competition_name = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('competition_id', 'student')
