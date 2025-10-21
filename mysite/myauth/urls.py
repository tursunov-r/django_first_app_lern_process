from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    MyLogoutView,
    AboutMeView,
    AboutMeUpdateView,
    RegisterView,
    UserListView,
    UserDetailView,
    UserAvatarUpdateView,
    HelloView,
)

app_name = "myauth"

urlpatterns = [
    # path("login/", login_view, name="login"),
    path("hello/", HelloView.as_view(), name="hello"),
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    # path("logout/", logout_view, name="logout"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("about-me/update/", AboutMeUpdateView.as_view(), name="update-about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path(
        "users/<int:pk>/update-avatar/",
        UserAvatarUpdateView.as_view(),
        name="user-avatar-update",
    ),
    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("session/set/", set_session_view, name="session-set"),
    path("session/get/", get_session_view, name="session-get"),
]
