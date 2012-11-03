from django.conf import settings
from django.conf.urls import patterns, url

from content.views import serve_content

urlpatterns = patterns('',
    url(r'^(?P<path>.*)$', serve_content, {
            'document_root': settings.CONTENT_DIR,
    })
)
