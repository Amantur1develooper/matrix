"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path,re_path
from django.conf import settings 
from django.conf.urls.static import static
from core.views import contacts,cart_remove2, about_us, install_settings, main_sevice, org_obsluj, remonorg, remontpk, sales_view, warranty,dostavka_oplata, home,category_view,test_email, product_detail,checkout,cart_detail,cart_add,cart_remove
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

# class StaticViewSitemap(Sitemap):
#     def items(self):
#         return [
#             'home',
#             'contacts',
#             'dostavka_oplata',
#             'warranty',
#             'about_us',
#             'main_sevice',
#             'sales',
#             'remontpk',
#             'remonorg',
#             'install_settings',
#             'org_obsluj',
#             'checkout',
#             'cart_detail',
#         ] # или свои URL name

#     def location(self, item):
#         return reverse(item)

# from rollyourown.seo.admin import register_seo_admin
from django.contrib import admin
# from .seo import MyMetadata

# register_seo_admin(admin.site, MyMetadata)
sitemaps = {'static': StaticViewSitemap}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-email/', test_email, name='test_email'),
    path('',home,name='home'),
    path('category/<slug:slug>/', category_view, name='category'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    
    path('contacts/',contacts,name='contacts'),
    path('dostavka_oplata/',dostavka_oplata, name='dostavka_oplata'),
    path('warranty/',warranty,name="warranty"),
    path('about_us/',about_us ,name='about_us'),
    path('main_sevice/',main_sevice,name='main_sevice'),
    path('sales/', sales_view, name='sales'),
    
    re_path(r'^robots\.txt$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),


    
    path('remontpk/', remontpk, name='remontpk'),
    path('remonorg/',remonorg,name='remonorg'),
    path('install_settings/', install_settings, name='install_settings'),
    path('org_obsluj/', org_obsluj, name='org_obsluj'),
    
    path('checkout/', checkout, name='checkout'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('cart/remove2/<int:product_id>/',cart_remove2,name='cart_remove2')
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
