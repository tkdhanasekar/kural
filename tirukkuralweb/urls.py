"""tirukkuralweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from kural.views import KuralPageView, SignupPageView, LoginPageView, LogoutView, activate, \
    MykuralsView, UserkuralsView, JudgeView, EvaluationView, RegistrationView, GenericHomeView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignupPageView.as_view(), name='signup'),
    path('kural/', KuralPageView.as_view(), name='kuralhome'),
    path('', GenericHomeView.as_view(), name='home'),
    path('download', MykuralsView.as_view(), name='mykural'),
    path('userkurals', UserkuralsView.as_view(), name='userskural'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('judge', JudgeView.as_view(), name='judge'),
    path('judge/<str:id>/report', EvaluationView.as_view(), name='evaluate'),
    path('register/', RegistrationView.as_view(), name='register'),
]
