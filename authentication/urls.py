from .views import RegistrationView,VerificationView,CompletePasswordreset,UsernameValidationView,EmailValidationView,LoginView,LogoutView,RequestPasswordView, ProfileView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('register',RegistrationView.as_view(),name="register"),
    path('login',LoginView.as_view(),name="login"),
    path('logout',LogoutView.as_view(),name="logout"),
    path('validate-username',csrf_exempt(UsernameValidationView.as_view()),name="validate-username"),
    path('request-reset-link',RequestPasswordView.as_view(),name='request-reset-link'),
    path('validate-email',csrf_exempt(EmailValidationView.as_view()),name="validate-email"),
    path('set-new-password/<uidb64>/<token>',csrf_exempt(CompletePasswordreset.as_view()),name='reset-user-password'),
    path('activate/<uidb64>/<token>',csrf_exempt(VerificationView.as_view()),name="activate"),
    path('profile',csrf_exempt(ProfileView.as_view()),name="profile")
]