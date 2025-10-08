import json
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth import authenticate, logout, login

from django.contrib.auth.tokens import default_token_generator

from django.utils.http import urlsafe_base64_decode
from kural.models import Tirukkural, UserKurals, MyUser, Students, \
    KuralMarks, StudentCompetition, CompetitionDate, Registration

from django.template.loader import render_to_string
from django.http import JsonResponse
from weasyprint import HTML
from datetime import datetime, timedelta


# Create your views here.

class SignupPageView(View):
    """
        endpoint: /signup
        purpose: "handles signup of an user"
    """
    def get(self, request):
        """

        :param request: None
        :return: render signup form with fields email, first_name, last_name, passowrd
        """
        template_name = 'signup.html'
        context = {"signup_page": "active"}
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, template_name=template_name, context=context)

    def post(self, request):
        """
        :param request: student_id, family_id and password, confirm_password are mandatory to this api
        :return: sends success message if signup success, else display error messages
        """
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        family_id = request.POST.get('family_id')
        c_password = request.POST.get('password_confirmation')
        if c_password != password:
            context = {"signup_page": "active", "messages": {"level": "danger", "short": "Error!",
                                                             "msg": "Password doesn't match with confirm password"}}
            return render(request, template_name='signup.html', context=context)

        user = MyUser.objects.filter(student_id=student_id)

        if user.exists():
            context = {"signup_page": "active", "messages": {"level": "danger", "short": "Error!",
                                                             "msg": "User with Student_id already exists"}}
            return render(request, template_name='signup.html', context=context)
        elif student_id and family_id and password:
            students_obj = Students.objects.filter(student_id=student_id, family_id=family_id)
            if students_obj.exists():
                students_obj = students_obj.first()
                student_full_name = students_obj.student_full_name
                student_class_level = students_obj.class_levels
                user = MyUser()
                user.student_id = student_id
                user.family_id = family_id
                user.student_full_name = student_full_name
                user.class_levels = student_class_level
                user.set_password(password)
                user.is_active = True
                user.save()
            else:
                context = {"signup_page": "active", "messages": {"level": "danger", "short": "Error!",
                                                                 "msg": "Student ID and Family ID not found , "
                                                                        "Contact school Admin"}}
                return render(request, template_name='signup.html', context=context)
            #email part
            # mail_subject = 'Activate your user account.'
            # current_site = get_current_site(request)
            # print(f"**********************************************")
            # message = render_to_string('acc_active_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': default_token_generator.make_token(user),
            # })
            # print(f"message: {message}")
            # to_email = email
            # email = EmailMessage(
            #     mail_subject, message, to=[to_email]
            # )
            #email.send()
            context = {"signup_page": "active", "messages": {"level": "success", "short": "Success! ",
                                                             "msg": "User Created Successfully. Now Login"}}
            return render(request, template_name='signup.html', context=context)

        return


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = MyUser._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


class LoginPageView(View):
    """
        endpoint: /login
        purpose: to authenticate users
    """

    def get(self, request):
        """
        :param request: None
        :return: render login form with username and password fields
        """
        template_name = 'login.html'
        context = {"login_page": "active"}
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, template_name=template_name, context=context)

    def post(self, request):
        """
        :param request: email, password are needed to authenticate
        :return: if login success redirect to another page else display error message
        """

        template_name = 'login.html'
        context = {"login_page": "active"}
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        user = MyUser.objects.filter(student_id=student_id).first()
        if user is not None and not user.is_active:
            context["messages"] = {"msg": "Email Verification Pending", "level": "danger", "short": "Error! "}
            return render(request=request, template_name=template_name, context=context)

        if user is not None:
            # A backend authenticated the credentials
            user = authenticate(student_id=student_id, password=password)
            if user and user.is_authenticated:
                login(request, user)
                context["messages"] = {"msg": "login successful", "level": "success", "short": "Success! "}
                return redirect(self.request.GET.get('next', '/'))

            else:
                context["messages"] = {"msg": "wrong password", "level": "danger", "short": "Error! "}
                return render(request=request, template_name=template_name, context=context)
        else:
            # No backend authenticated the credentials
            context["messages"] = {"msg": "User not found", "level": "danger", "short": "Error! "}
            return render(request=request, template_name=template_name, context=context)


class LogoutView(View):
    """
        endpoint: /logout
        purpose: Handles logout of an user
    """
    def get(self, request):
        """
        :param request: request headers
        :return: renders login page
        """
        logout(request)
        return redirect('/login')


class KuralPageView(View):
    """
        endpoint: /kural
        purpose: this handles Kural page views
    """
    def get(self, request):
        """
        :param request: None
        :return: render home page
        """
        template_name = 'home.html'
        context = {"kural_page": "active"}
        if not request.user.is_authenticated:
            return redirect('/')

        # check user is registered for is_kural_interested
        context['user'] = request.user
        context["is_kural_interested"] = False
        context["event_cutoff_date"] = False
        # check registration and get the selected competitions from tables
        comp_obj = CompetitionDate.objects.filter(is_active=True)
        if comp_obj.exists():
            competition = comp_obj.first()
            if competition.cutoff_date <= datetime.now().date():
                context["event_cutoff_date"] = True
            reg = Registration.objects.filter(student=request.user,
                                              competition_id=competition.id)
            if reg.exists():
                reg = reg.first()
                context['registration'] = reg
                context['competition'] = competition
                context["is_kural_interested"] = reg.is_kural_interested

                # redirect non kural selected users to home they are not allowed in this page
                if not context["is_kural_interested"]:
                    return redirect('/')

                kurals = list(Tirukkural.objects.all())
                kural_ids_list = list()

                groups = [group.name for group in request.user.groups.all()]
                if 'student' in groups:
                    user_kural_obj = UserKurals.objects.filter(user=request.user,
                                                               created_on__gte=competition.created_on)
                    if user_kural_obj.exists():
                        user_kural_obj = user_kural_obj.first()
                        kural_ids_list = user_kural_obj.kural_ids.split(',')

                    master_list = []
                    for item in kurals:
                        if str(item.kural_id) in kural_ids_list:
                            item.selected = True
                        else:
                            item.selected = False
                        master_list.append(item)
                    context["kurals"] = master_list
                    context["kural_count"] = len(kural_ids_list)
        return render(request=request, template_name=template_name, context=context)


class UserkuralsView(View):
    """
        endpoint: /userkurals
        purpose: this handles mykurals page views
    """

    def get(self, request):
        """
        :param request: None
        :return: json list of kural ids
        """
        kural_ids_list = []
        if not request.user.is_authenticated:
            return JsonResponse(data=kural_ids_list, safe=False)
        # Get current year selections alone (ignore previous year selections)
        kural_obj = UserKurals.objects.filter(user=request.user, year=datetime.now().date().year)
        if kural_obj.exists():
            kural_ids_list = kural_obj.first().kural_ids.split(',')
        return JsonResponse(data=kural_ids_list, safe=False)


class MykuralsView(View):
    """
        endpoint: /mykurals
        purpose: this handles mykurals page views
    """
    def get(self, request):
        """
        :param request: None
        :return: render home page
        """
        template_name = 'mykural.html'
        context = {"mykural_page": "active"}
        if not request.user.is_authenticated:
            return redirect('/login')

        # check user is registered for is_kural_interested
        context['user'] = request.user
        context["is_kural_interested"] = False
        context["event_cutoff_date"] = False

        # check registration and get the selected competitions from tables
        comp_obj = CompetitionDate.objects.filter(is_active=True)
        if comp_obj.exists():
            competition = comp_obj.first()
            if competition.cutoff_date <= datetime.now().date():
                context["event_cutoff_date"] = True
            reg = Registration.objects.filter(student=request.user,
                                              competition_id=competition.id)
            if reg.exists():
                reg = reg.first()
                context["registration"] = reg
                context["is_kural_interested"] = reg.is_kural_interested

        # redirect non kural selected users to home they are not allowed in this page
        if not context["is_kural_interested"]:
            return redirect('/')

        kural_obj = UserKurals.objects.filter(user=request.user)
        pdf_path = None
        if kural_obj.exists():
            kural_obj = kural_obj.last()
            pdf_path = kural_obj.pdf_path
        context["pdf_path"] = pdf_path
        return render(request=request, template_name=template_name, context=context)

    def post(self, request):
        """
        param: kural_ids: ['1', '190', '1330']
        return redirect('/mykurals')
        """
        if not request.user.is_authenticated:
            return redirect('/login')
        kural_ids_list = json.loads(request.body.decode("utf-8"))
        # create or update entry
        year = datetime.now().year
        user_kural_obj = UserKurals.objects.filter(user=request.user, year=year)
        if user_kural_obj.exists():
            user_kural_obj = user_kural_obj.first()
            old_kural_ids = user_kural_obj.kural_ids.split(',')
            #kural_ids_list.extend(old_kural_ids)
        else:
            user_kural_obj = UserKurals(user=request.user, year=year)

        kural_ids = ",".join(kural_ids_list)
        user_kural_obj.kural_ids = kural_ids
        # Get user selected kurals here
        kuralobj = Tirukkural.objects.filter(kural_id__in=kural_ids_list)
        kurals_values = [{"line_1": item.line_1, "line_2": item.line_2, "kural_id": item.kural_id, "munnurai": item.munnurai, "select_order": kural_ids_list.index(str(item.kural_id))} for item in kuralobj]

        kurals = sorted(kurals_values, key=lambda d: d['select_order'])

        # user file
        user_file = f"userpdfs/{request.user.class_levels}-{request.user.student_full_name}-{request.user.student_id}-{year}.pdf"
        # Rendered

        html_string = render_to_string('pdf_template.html', {'kurals': kurals,
                                                             'date': datetime.now().date,
                                                             'user': request.user
                                                             })
        html = HTML(string=html_string)
        result = html.write_pdf(user_file)

        # save kural obj
        pdf_path = "/" + user_file
        user_kural_obj.pdf_path = pdf_path
        user_kural_obj.save()
        return JsonResponse(data={}, safe=True)


class JudgeView(View):
    """
        endpoint: /judge
        purpose: this handles judge page views
    """
    def get(self, request):
        """
        :param request: None
        :return: render home page
        """
        template_name = 'judge.html'
        context = {"judge_page": "active"}
        groups = [group.name for group in request.user.groups.all()]
        judge = False
        # if 'judge1' in groups:
        #     judge = True
        # if 'judge2' in groups:
        #     judge = True
        # if not request.user.is_authenticated or not judge:
        #     print(f"Here redirecting to user")
        #     return redirect('/login')
        # # query userkurals and get user_ids and kural ids
        # #  myuser_obj = MyUser.objects.filter(groups__name='student').order_by('student_full_name')
        # student_obj = AssignStudent.objects.filter(judge=request.user)
        # if student_obj.exists():
        #     student_ids = [item.student_id for item in student_obj]
        #     print(f"{student_ids}")
        #     user_kural_obj = UserKurals.objects.filter(user__student_id__in=student_ids)
        #     print(f"||||||||{user_kural_obj.count()}")
        # else:
        #     user_kural_obj = []
        # level_set = set()
        # user_dict = {}
        # for user_kural in user_kural_obj:
        #     level_set.add(user_kural.user.class_levels)
        #     user_dict[user_kural.user.id] = {"name": user_kural.user.student_full_name,
        #                                      "level": user_kural.user.class_levels,
        #                                      "student_id": user_kural.user.student_id,
        #                                      "count": len(user_kural.kural_ids.split(',')),
        #                                      "id": user_kural.user.id
        #                                      }
        # context['levels'] = list(level_set)
        # context['users_data'] = user_dict
        # print(f"****level set{level_set}")
        return render(request=request, template_name=template_name, context=context)


class EvaluationView(View):
    """
        endpoint: /judge/<user_kural_id>/report
        purpose: this handles judge page views
    """
    def get(self, request, id):
        """
        :param request: None
        :return: render home page
        """
        template_name = 'evaluate.html'
        context = {"judge_page": "active"}
        groups = [group.name for group in request.user.groups.all()]
        judge_flag = False
        judge = request.user
        if 'judge1' in groups:
            judge_flag = True
        if 'judge2' in groups:
            judge_flag = True
        if not request.user.is_authenticated or not judge_flag:
            return redirect('/login')
        try:
            user_marks = KuralMarks.objects.filter(judge=judge, user__id=id)
            kurals_list = list()
            if user_marks.exists():
                for item in user_marks:
                    di = dict()
                    di["kural_id"] = item.kural_id
                    di["tirukkural"] = item.tirukkural
                    di["munnurai"] = item.munnurai
                    di["judge_kural_marks"] = item.judge_kural_marks
                    di["judge_porul_marks"] = item.judge_porul_marks
                    di["mark_id"] = item.id
                    kurals_list.append(di)
            else:
                user = MyUser.objects.get(id=id)
                user_kural_obj = UserKurals.objects.get(user=user)
                kural_ids = user_kural_obj.kural_ids.split(',')
                kurals = Tirukkural.objects.filter(kural_id__in=kural_ids)

                for item in kurals:
                    kural_id = item.kural_id
                    tirukkural = item.line_1 + "\n" + item.line_2
                    munnurai = item.munnurai
                    km_obj = KuralMarks(user=user, judge=judge)
                    km_obj.kural_id = kural_id
                    km_obj.tirukkural = tirukkural
                    km_obj.munnurai = munnurai
                    km_obj.judge_kural_marks = 0
                    km_obj.judge_porul_marks = 0
                    km_obj.save()
                    di = dict()
                    di["kural_id"] = kural_id
                    di["tirukkural"] = tirukkural
                    di["munnurai"] = munnurai
                    di["judge_kural_marks"] = 0
                    di["judge_porul_marks"] = 0
                    km_obj.save()
                    di["mark_id"] = km_obj.id
                    kurals_list.append(di)
            context['kurals'] = kurals_list
            context["id"] = id
            return render(request=request, template_name=template_name, context=context)
        except Exception as e:
            print(f"{e}")

    def post(self, request, id):
        """
        :param request: id
        :return: render home page
        """
        template_name = 'evaluate.html'
        context = {"judge_page": "active"}
        groups = [group.name for group in request.user.groups.all()]
        judge = False
        if 'judge1' in groups:
            judge = True
        if 'judge2' in groups:
            judge = True
        if not request.user.is_authenticated or not judge:
            return redirect('/login')
        try:
            received_json_data = json.loads(request.body.decode("utf-8"))
            data = received_json_data["results"]
            for item in data:
                km_obj = KuralMarks.objects.get(id=int(item["mark_id"]))
                km_obj.judge_kural_marks = float(item["kural_marks"])
                km_obj.judge_porul_marks = float(item["porul_marks"])
                km_obj.save()
            return JsonResponse(data={}, safe=True)
        except Exception as e:
            print(f"{e}")


class RegistrationView(View):
    """
        endpoint: /registration
        purpose: "handles registration of a user who is logged in "
    """
    def get(self, request):
        """

        :param request: None
        :return: render signup form with fields email, first_name, last_name, passowrd
        """
        template_name = 'registration_form.html'
        context = {"register_page": "active"}
        if not request.user.is_authenticated:
            return redirect('/')
        context['user'] = request.user
        context["is_registered"] = False
        class_levels = request.user.class_levels
        context["student_id"] = request.user.student_full_name
        context["class_levels"] = class_levels
        competitions = list(StudentCompetition.objects.filter(class_levels=class_levels, is_active=True).order_by('created_on').values_list('name', flat=True))
        context['competitions'] = competitions
        event_dates = CompetitionDate.objects.filter(is_active=True)
        context["block_registration"] = False
        context["is_kural_interested"] = False
        context["event1_date_show"] = False
        context["event2_date_show"] = False 
        if event_dates.exists():
            event_date_obj = event_dates.first()
            if event_date_obj.event1_date:
                context["event1_date"] = event_date_obj.event1_date.strftime("%d-%b-%Y")
                context["event1_date_show"] = True
            if event_date_obj.event2_date:
                context["event2_date"] = event_date_obj.event2_date.strftime("%d-%b-%Y")
                context["event2_date_show"] = True
            cutoff_date = event_date_obj.cutoff_date
            context["cutoff_date"] = cutoff_date               
            if cutoff_date < datetime.now().date():
                context["block_registration"] = True
            reg = Registration.objects.filter(student=request.user,
                                              competition_id=event_date_obj.id)
            if reg.exists():
                reg = reg.first()
                context["is_registered"] = True
                context["is_kural_interested"] = reg.is_kural_interested
                context["competition_name"] = reg.competition_name
        return render(request, template_name=template_name, context=context)

    def post(self, request):
        """
        :param request: student, class_levels, is_kural_interested, competition are mandatory to this api
        :return: sends success message if registration success, else display error messages
        """
        template_name = 'registration_form.html'
        context = {"register_page": "active"}
        if not request.user.is_authenticated:
            return redirect('/')
        context['user'] = request.user
        context["is_registered"] = False
        context["is_kural_interested"] = False
        student = request.user
        class_levels = request.user.class_levels
        is_kural_form = request.POST.get('is_kural_interested')
        is_kural_interested = None
        if is_kural_form == 'true':
            is_kural_interested = True
        elif is_kural_form == 'false':
            is_kural_interested = False
        else:
            is_kural_interested = None
        competition = request.POST.get('competition')
        comp_id_obj = CompetitionDate.objects.filter(is_active=True)
        if comp_id_obj.exists():
            comp_id_obj = comp_id_obj.first()
        else:
            comp_id_obj = CompetitionDate.objects.last()
        comp_id = int(comp_id_obj.id)
        cutoff_date = comp_id_obj.cutoff_date
        context["student_id"] = request.user.student_id
        context["class_levels"] = class_levels
        context["block_registration"] = False
        competitions = list(StudentCompetition.objects.filter(class_levels=class_levels).order_by('created_on').values_list('name', flat=True))
        context['competitions'] = competitions
        if cutoff_date < datetime.now().date():
            context["block_registration"] = True
            raise Exception("Registration date is over")
        # 2023 no second competition hence commenting this part of the code
        if not competition and comp_id_obj.event2_date:
            context["messages"] = {"msg": "ஏதேனும் ஒரு போட்டியை தேர்ந்தெடுக்கவும்", "level": "danger", "short": "பிழை! "}
            return render(request=request, template_name=template_name, context=context)
        if comp_id_obj.event1_date and is_kural_interested is None:
            context["messages"] = {"msg": "திருக்குறள் போட்டியில் பங்கு பெற விருப்பமா?", "level": "danger", "short": "பிழை! "}
            return render(request=request, template_name=template_name, context=context)
        try:
            registration_obj, created = Registration.objects.get_or_create(competition_id=comp_id,
                                                                           student=student, class_levels=class_levels)
            registration_obj.is_kural_interested = is_kural_interested if is_kural_interested is not None else False
            registration_obj.competition_name = competition
            registration_obj.save()
            return redirect('/')
        except Exception as e:
            msg = f"{str(e)}"
            context["messages"] = {"msg": msg, "level": "danger", "short": "Error! "}
            return render(request=request, template_name=template_name, context=context)


class GenericHomeView(View):
    """
        endpoint: /
        purpose: generic home page for all users
    """

    def get(self, request):
        """
        :param request: None
        :return: render login form with username and password fields
        """
        template_name = 'generic_home.html'
        context = {"home_page": "active"}
        if not request.user.is_authenticated:
            return redirect('/login')
        context['user'] = request.user
        context["is_registered"] = False
        context["is_kural_interested"] = False
        # check registration and get the selected competitions from tables
        comp_obj = CompetitionDate.objects.filter(is_active=True)
        if comp_obj.exists():
            competition = comp_obj.first()
            reg = Registration.objects.filter(student=request.user,
                                              competition_id=competition.id)
            if reg.exists():
                context["is_registered"] = True
                reg = reg.first()
                context['registration'] = reg
                context['competition'] = competition
                context["is_kural_interested"] = reg.is_kural_interested

        return render(request, template_name=template_name, context=context)
