from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.i18n import patterns as i18n_patterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

calculation_pattern = r'^contamination/(?P<dvs_id>\d+)/' + \
                       '(?P<substance_id>\d+)/(?P<wind>\d{1,2}[,\.]?\d?)/' + \
                       '(?P<temperature>[-]?\d{1,2})/' + \
                       '(?P<mass>\d{1,4})/calculate/$'

urlpatterns = i18n_patterns('',
    # Examples:
    # url(r'^$', 'environ.views.home', name='home'),
    # url(r'^environ/', include('environ.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),   
    url(r'^initialize/', 'contamination.initializer.initialize'), 
)

urlpatterns += patterns('contamination.views',
    url(calculation_pattern, 
         'calculate'),                            
    url(r'^languages/(?P<language>\w{2})', 'indexWithLanguage'),
    url(r'^$', 'index'),
)
  
