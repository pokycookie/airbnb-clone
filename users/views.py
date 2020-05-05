import os
import requests
from django.http import QueryDict
from django.views.generic import FormView, DetailView, UpdateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            messages.add_message(self.request, messages.SUCCESS, "Login Success!")
            return reverse("core:home")


class LogoutView(LogoutView):
    def get_next_page(self):
        next_page = reverse_lazy("core:home")
        messages.success(self.request, "See you later!")
        return next_page


class SignUpView(mixins.LoggedOutOnlyView, FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    # Auto Login
    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, "SignUp Success!")
            messages.success(self.request, "Thank you to with us!")
        user.verify_email()  # send email
        return super().form_valid(form)


# Email Verification
def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_authKey=key)
        user.email_verified = True
        user.email_authKey = ""
        user.save()
        # to do: add success message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    q = QueryDict(mutable=True)
    q["client_id"] = os.environ.get("GITHUB_ID")
    q["redirect_uri"] = "http://127.0.0.1:8000/users/login/github/callback"
    q["scope"] = "read:user"
    query_string = q.urlencode()
    return redirect("https://github.com/login/oauth/authorize?" + query_string)


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        code = request.GET.get("code", None)
        q = QueryDict(mutable=True)
        q["client_id"] = os.environ.get("GITHUB_ID")
        q["client_secret"] = os.environ.get("GITHUB_SECRET")
        q["code"] = code
        query_string = q.urlencode()
        if code is not None:
            result = requests.post(
                "https://github.com/login/oauth/access_token?" + query_string,
                headers={"Accept": "application/json"},
            )
            result_json = result.json()
            error = result_json.get("error", None)
            if error is not None:
                raise GithubException("Login Fail")
            else:
                access_token = result_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    if name is None:
                        name = "None"
                    email = profile_json.get("email")
                    if email is None:
                        email = "None"
                    bio = profile_json.get("bio")
                    if bio is None:
                        bio = "None"
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                f'Login Fail. Please Login with "{user.login_method}"'
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            username=email,
                            first_name=name,
                            bio=bio,
                            email=email,
                            login_method=models.User.LOGIN_GITHUB,
                        )
                        if email != "None":
                            user.email_verified = True
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, "Login Success!")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Login Fail")
        else:
            raise GithubException("Login Fail")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    q = QueryDict(mutable=True)
    q["client_id"] = os.environ.get("KAKAO_ID")
    q["redirect_uri"] = "http://127.0.0.1:8000/users/login/kakao/callback"
    q["response_type"] = "code"
    query_string = q.urlencode()
    return redirect("https://kauth.kakao.com/oauth/authorize?" + query_string)


class Kakao_Exception(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code", None)
        q = QueryDict(mutable=True)
        q["grant_type"] = "authorization_code"
        q["client_id"] = os.environ.get("KAKAO_ID")
        q["redirect_uri"] = "http://127.0.0.1:8000/users/login/kakao/callback"
        q["code"] = code
        query_string = q.urlencode()
        if code is not None:
            token_request = requests.post(
                "https://kauth.kakao.com/oauth/token?" + query_string
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise Kakao_Exception("Login Fail.")
            access_token = token_json.get("access_token")
            profile_request = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_json = profile_request.json()
            email = profile_json.get("kakao_account").get("email", None)
            if email is None:
                raise Kakao_Exception("Login Fail.", "Please agree for use email")
            nickname = (
                profile_json.get("kakao_account").get("profile").get("nickname", None)
            )
            profile_image = (
                profile_json.get("kakao_account")
                .get("profile")
                .get("profile_image_url", None)
            )
            try:
                user = models.User.objects.get(email=email)
                if user.login_method != models.User.LOGIN_KAKAO:
                    raise Kakao_Exception(
                        "Login Fail.", f'Please Login with "{user.login_method}"',
                    )
            except models.User.DoesNotExist:
                user = models.User.objects.create(
                    username=email,
                    email=email,
                    first_name=nickname,
                    login_method=models.User.LOGIN_KAKAO,
                    email_verified=True,
                )
                user.set_unusable_password()
                user.save()
                if profile_image is not None:
                    photo_request = requests.get(profile_image)
                    user.avatar.save(
                        f"{nickname}-avatar", ContentFile(photo_request.content)
                    )
                    print("avatar" * 20, profile_image)
            login(request, user)
            messages.success(request, "Login Success!")
            return redirect(reverse("core:home"))
    except Kakao_Exception as e:
        for i in e.args:
            messages.error(request, i)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"


class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "first_name",
        "last_name",
        "nickname",
        "avatar",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )
    success_message = "Profile updated successfully"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["first_name"].widget.attrs = {"placeholder": "First Name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last Name"}
        form.fields["nickname"].widget.attrs = {"placeholder": "Nickname"}
        form.fields["bio"].widget.attrs = {"placeholder": "Introduce yourself"}
        form.fields["birthdate"].widget.attrs = {"placeholder": "0000-00-00 (BirthDay)"}
        return form


class UpdatePasswordView(
    mixins.EmailLoginOnlyView, SuccessMessageMixin, PasswordChangeView,
):

    template_name = "users/update-password.html"
    success_url = reverse_lazy("users:update-profile")
    success_message = "Password Updated Successfully!"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current Password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New Password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm New Password"
        }
        return form
