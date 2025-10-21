from random import random

from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DetailView,
    FormView,
)
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page

from .models import Profile
from .forms import ProfileForm


class HelloView(View):

    welcome_message = _("welcome message world")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext("one product", "{count} products", items)
        products_line = products_line.format(count=items_str)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>" f"\n<h2>{products_line}</h2>"
        )


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class AboutMeUpdateView(UpdateView):
    """
    View для обновления аватарки пользователя со страницы about-me
    """

    model = Profile
    fields = ["avatar"]
    template_name = "myauth/update-about-me.html"

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_success_url(self):
        return reverse("myauth:about-me")


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super(RegisterView, self).form_valid(form)
        Profile.objects.get_or_create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user=user)
        return response


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")
    http_method_names = ["get", "post", "options", "head"]

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class UserListView(ListView):
    """
    Для отображения всех пользователей,
    что бы администратор мог изменить аватарку пользователя
    """

    model = User
    template_name = "myauth/user-list.html"
    context_object_name = "users"


class UserDetailView(DetailView):
    """открывает детали пользователя админу из страницы users"""

    model = User
    template_name = "myauth/user-detail.html"
    context_object_name = "user_obj"


class UserAvatarUpdateView(FormView):
    """Смена аватара, действие позволено только администратору"""

    template_name = "myauth/user-avatar-update.html"
    form_class = ProfileForm

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=self.kwargs["pk"])
        if not (request.user.is_staff or request.user == self.user_obj):
            return HttpResponseForbidden("You are not allowed to edit this profile.")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        profile, _ = Profile.objects.get_or_create(user=self.user_obj)
        return {
            "bio": profile.bio,
            "first_name": self.user_obj.first_name,
            "last_name": self.user_obj.last_name,
            "email": self.user_obj.email,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_obj"] = self.user_obj  # передаём в шаблон
        return context

    def form_valid(self, form):
        profile, _ = Profile.objects.get_or_create(user=self.user_obj)
        profile.avatar = form.cleaned_data["avatar"]
        profile.save()
        # если форма редактирует first_name/last_name/email
        # на будущее если пригодится
        self.user_obj.first_name = form.cleaned_data.get(
            "first_name", self.user_obj.first_name
        )
        self.user_obj.last_name = form.cleaned_data.get(
            "last_name", self.user_obj.last_name
        )
        self.user_obj.email = form.cleaned_data.get("email", self.user_obj.email)
        self.user_obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("myauth:user-detail", kwargs={"pk": self.user_obj.pk})


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
