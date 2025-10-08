from rolepermissions.roles import AbstractUserRole

class Student(AbstractUserRole):
    available_permissions = {
        'create_user_kurals_record': True,
    }


class Judge(AbstractUserRole):
    available_permissions = {
        'create_student_report_record': True,
    }