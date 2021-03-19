from django.urls import path, re_path
from .views import ProductCreateView, ProductOperationsView, AddToCartView, SearchAPIView, DisplayByOrder, \
    PlaceOrderAPIView

urlpatterns = [
    path('', ProductCreateView.as_view(), name='create'),
    path('<int:id>', ProductOperationsView.as_view(), name="product-operation"),
    path('cart/<int:id>', AddToCartView.as_view(), name="cart"),
    # path('order/low', OrderAscendingAPIView.as_view(), name="order-low"),
    # path('order/high', OrderDescendingAPIView.as_view(), name="order-high"),
    # path('search/', SearchAPIView.as_view(), name="search"),
    re_path('^search/(?P<item>.+)/$', SearchAPIView.as_view()),
    re_path('^order/(?P<type>.+)/$', DisplayByOrder.as_view()),
    path('place-order/', PlaceOrderAPIView.as_view())
]
