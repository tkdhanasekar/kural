from django.contrib import admin
from kural.models import UserKurals, Tirukkural, MyUser, \
    Students,CompetitionDate, Registration, StudentCompetition

from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportMixin
from import_export.fields import Field
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from admin_auto_filters.filters import AutocompleteFilter
from django_admin_listfilter_dropdown.filters import DropdownFilter




# Register your models here.

class UserFilter(AutocompleteFilter):
    title = 'User' # display title
    field_name = 'student' 


class MyUserFilter(AutocompleteFilter):
    title = 'User' # display title
    field_name = 'user' 


class MyUserlistResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        value = row['password']
        print("************** before import row called", value)
        if not value.startswith('pbkdf2_sha256$'):
            row['password'] = make_password(value)

    def after_save_instance(self, instance, using_transactions, dry_run):
        if not instance.groups.exists():
            instance.groups.add(Group.objects.get(name='student'))
        print("************** after save came", instance.groups.all())
        return instance

    # def skip_row(self, instance, original):
    #     user_obj = MyUser.objects.filter(student_id=instance.student_id)
    #     return user_obj.exists()

    class Meta:
        model = MyUser
        skip_unchanged = True
        # report_skipped = False
        fields = ('student_id', 'family_id', 'class_levels', 'student_full_name', 'password', )
        import_id_fields = ['student_id']


class MyUserAdmin(ImportExportModelAdmin):
    date_hierarchy = 'created_on'
    resource_class = MyUserlistResource
    list_display = ('student_id', 'student_full_name', 'class_levels',)
    list_filter = (('class_levels', DropdownFilter),)
    ordering = ['created_on']
    search_fields = ['student_id', 'student_full_name']

    def save_model(self, request, obj, form, change):
        print(f"*************called save***********", form)
        if not obj.password.startswith('pbkdf2_sha256$'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


class StudentsResource(resources.ModelResource):
    class Meta:
        model = Students
        skip_unchanged = True
        report_skipped = False
        fields = ('student_id', 'student_full_name', 'class_levels', 'family_id')
        import_id_fields = ['student_id', 'student_full_name', 'class_levels', 'family_id']


class StudentsAdmin(ImportExportModelAdmin):
    resource_class = StudentsResource
    list_display = ('student_id', 'family_id', 'student_full_name', 'class_levels')
    list_filter = ('created_on', 'class_levels')
    ordering = ['created_on']
    search_fields = ['student_id', 'student_full_name', 'family_id']


class UserKuralsResource(resources.ModelResource):
    show_kural_count = Field()

    class Meta:
        model = UserKurals
    
    def dehydrate_show_kural_count(self, inst):
        return len(inst.kural_ids.split(','))


class UserKuralsAdmin(ExportMixin, admin.ModelAdmin,):
    resources_class = [UserKuralsResource]
    date_hierarchy = 'created_on'
    list_display = ('user', 'show_kural_count', 'kural_ids', 'pdf_path', 'created_on', 'updated_on', )
    list_filter = ( MyUserFilter,)
    search_fields = ['user__student_full_name', 'kural_ids']

    def show_kural_count(self, inst):
        return len(inst.kural_ids.split(','))

    show_kural_count.admin_order_field = 'show_kural_count'


class TirukkuralAdmin(admin.ModelAdmin):
    list_display = ('kural_id', 'line_1', 'line_2', 'munnurai')
    list_filter = (('kural_id', DropdownFilter), )
    search_fields = ['kural_id', 'line_1', 'line_2']


class CompetitionDateAdmin(admin.ModelAdmin):
    list_display = ('name', 'event1_date', 'event2_date', 'cutoff_date')
    list_filter = (('name', DropdownFilter), 'event1_date', 'event2_date', 'is_active')
    search_fields = ['name', 'event1_date', 'event2_date']


class RegistrationResource(resources.ModelResource):
    family_id = Field()
    student_full_name = Field()

    def dehydrate_family_id(self, reg):
        family_id = getattr(reg.student, "family_id", "unknown")
        return family_id

    def dehydrate_student_full_name(self, reg):
        student_full_name = getattr(reg.student, "student_full_name", "unknown")
        return student_full_name

    class Meta:
        model = Registration
        skip_unchanged = True
        report_skipped = False
        fields = ('student__student_id', 'family_id',  'class_levels', 'is_kural_interested', 'competition_name')
        import_id_fields = ['competition_id', 'student_id', 'family_id',  'class_levels', 'is_kural_interested', 'competition_name']
        export_order = ('student__student_id', 'family_id', 'student_full_name', 'class_levels', 'is_kural_interested',
                        'competition_name')


class RegistrationAdmin(ImportExportModelAdmin):
    resource_class = RegistrationResource
    date_hierarchy = 'created_on'
    list_display = ('student', 'class_levels', 'is_kural_interested', 'competition_name')
    list_filter = [ UserFilter, 
                   ('class_levels', DropdownFilter), 
                   ('is_kural_interested', DropdownFilter), 
                   ('competition_name', DropdownFilter),                   
                   ]
    search_fields = ['student__student_full_name', 'student__family_id', 'class_levels', 'competition_name']


class StudentCompetitionResource(resources.ModelResource):
    class Meta:
        model = StudentCompetition
        skip_unchanged = True
        report_skipped = False
        fields = ('class_levels', 'name')
        import_id_fields = ['class_levels', 'name']


class StudentCompetitionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = StudentCompetitionResource
    list_display = ('class_levels', 'name')
    list_filter = (('class_levels', DropdownFilter), ('name', DropdownFilter))
    search_fields = ['class_levels', 'name']



admin.site.register(MyUser, MyUserAdmin)
admin.site.register(UserKurals, UserKuralsAdmin)
admin.site.register(Tirukkural, TirukkuralAdmin)
admin.site.register(CompetitionDate, CompetitionDateAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(StudentCompetition, StudentCompetitionAdmin)

admin.site.site_header  =  "Kural Administration"  
admin.site.site_title  =  "Kural Administration"
admin.site.index_title  =  "Kural Admin Portal"