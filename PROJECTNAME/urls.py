from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', include("APPNAME.urls")), 
	]
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)