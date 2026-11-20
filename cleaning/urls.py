from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
 path("",views.home,name="home"), path("services/",views.catalog,name="catalog"),
 path("calculator/",views.calculator,name="calculator"), path("order/new/",views.order_create,name="order_create"),
 path("account/",views.account,name="account"), path("account/orders/<int:pk>/",views.order_detail,name="order_detail"),
 path("about/",views.about,name="about"), path("search/",views.search,name="search"),
 path("register/",views.register,name="register"),
 path("login/",auth_views.LoginView.as_view(template_name="cleaning/login.html"),name="login"),
 path("logout/",auth_views.LogoutView.as_view(),name="logout"), path("api/price/",views.price_api,name="price_api"),
]
