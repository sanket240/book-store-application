from django.urls import path
from .views import ProductCreateView, ProductOperationsView

urlpatterns = [
    path('', ProductCreateView.as_view(), name='create'),
    path('<int:id>', ProductOperationsView.as_view(), name="notes")
    # path('otp-verify/', VerifyOTP.as_view(), name='otp-verify'),
    # path('login', LoginView.as_view(), name='login'),
]
