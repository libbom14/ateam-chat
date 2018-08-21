
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (login as auth_login, logout as auth_logout,
                                 REDIRECT_FIELD_NAME, authenticate)
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from .forms import LoginForm, SignupForm


log = logging.getLogger(__name__)


class LoginView(generic.FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = settings.LOGIN_REDIRECT_URL
    username = None

    def get(self, request, *args, **kwargs):
        self.username = request.GET.get('username')
        if request.user.is_authenticated():
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super(LoginView, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = super(LoginView, self).get_initial()
        if self.username:
            initial['username'] = self.username
        return initial

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)

        msg = '로그인 성공.'
        messages.success(self.request, msg)

        log.info(self.request, menu='user', action='login',
                 type=self.request.user.type)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        return context

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class SignupView(generic.FormView):
    form_class = SignupForm
    template_name = 'signup.html'
    success_url = reverse_lazy('about')

    def register_user(self, form):
        user = form.save()
        user = authenticate(username=user.username, password=form.cleaned_data['password1'])
        auth_login(self.request, user)
        return user

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super(SignupView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.register_user(form)
        user.save()
        return redirect(self.get_success_url())

