from django.urls import path, re_path
from django.conf.urls import  url
from .views import ProductCreateView, ProductOperationsView, AddToCartView, SearchAPIView, DisplayBySortedProducts, \
    PlaceOrderAPIView,AddToWishList

urlpatterns = [
    path('', ProductCreateView.as_view(), name='create'),
    path('<int:id>', ProductOperationsView.as_view(), name="product-operation"),
    path('cart/<int:id>', AddToCartView.as_view(), name="cart"),
    re_path('^search/(?P<item>.+)/$', SearchAPIView.as_view()),
    re_path('^sort/(?P<type>.+)/$', DisplayBySortedProducts.as_view()),
    path('place-order/', PlaceOrderAPIView.as_view()),
    path('wish/<int:id>', AddToWishList.as_view(), name="wish-list"),

]
