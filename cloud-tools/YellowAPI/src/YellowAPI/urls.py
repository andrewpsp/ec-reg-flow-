from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'YellowAPI.views.home', name='home'),
    # url(r'^YellowAPI/', include('YellowAPI.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	(r'^search$', 'business.views.search'),
    (r'^deals$', 'business.views.searchdeals'),
	(r'^(?P<id>\w+)$', 'business.views.details'),
	(r'', 'business.views.index'),
)
