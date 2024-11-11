from django.urls import path
from .views import *

urlpatterns = [
    # path('putdata/', Putbucketlist.as_view(), name='bucketlist'),
    path('process-tgz/', process_tgz, name='process-tgz'),
    path('search-logs/', search_logs, name='search-logs'),  # New search logs path

]
