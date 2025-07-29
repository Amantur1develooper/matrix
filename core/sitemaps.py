from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'home',
            'contacts',
            'dostavka_oplata',
            'warranty',
            'about_us',
            'main_sevice',
            'sales',
            'remontpk',
            'remonorg',
            'install_settings',
            'org_obsluj',
            'checkout',
            'cart_detail',
        ] # или свои URL name

    def location(self, item):
        return reverse(item)
