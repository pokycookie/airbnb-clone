from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy


class LoggedOutOnlyView(UserPassesTestMixin):

    permission_denied_message = "Wrong Access"

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.error(self.request, "Wrong Access")
        return redirect(reverse("core:home"))


class LoggedInOnlyView(LoginRequiredMixin):

    login_url = reverse_lazy("users:login")

    def test_func(self):
        return self.request.user.is_authenticated


class EmailLoginOnlyView(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.login_method == "email"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Wrong Access")
            messages.error(
                self.request,
                f"You can't change password, when you login with {self.request.user.login_method}",
            )
            return redirect(reverse("core:home"))
        else:
            return redirect(
                reverse("users:login") + "?next=" + reverse("users:update-password")
            )
