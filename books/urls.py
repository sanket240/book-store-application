from django.urls import path
from .views import ProductCreateView, ProductOperationsView, AddToCartView, OrderAscendingAPIView, \
    OrderDescendingAPIView, SearchAPIView

urlpatterns = [
    path('', ProductCreateView.as_view(), name='create'),
    path('<int:id>', ProductOperationsView.as_view(), name="notes"),
    path('cart/<int:id>', AddToCartView.as_view(), name="cart"),
    path('order/low', OrderAscendingAPIView.as_view(), name="order-low"),
    path('order/high', OrderDescendingAPIView.as_view(), name="order-high"),
    path('search', OrderDescendingAPIView.as_view(), name="order-high")

    # path('otp-verify/', VerifyOTP.as_view(), name='otp-verify'),
    # path('login', LoginView.as_view(), name='login'),
]
