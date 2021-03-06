"""hmmtuf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings

from .config import REGIONS_FILES_ROOT
from .config import REGIONS_FILES_URL
from .config import VITERBI_PATHS_FILES_URL
from .config import VITERBI_PATHS_FILES_ROOT
from .config import VITERBI_SEQ_COMPARISON_FILES_ROOT
from .config import VITERBI_SEQ_COMPARISON_FILES_URL

# urlpatterns for the HMMTuf application
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hmmtuf_home.urls')),
    path('load_file/', include('file_loader.urls')),
    path('compute/', include('hmmtuf_compute.urls')),

    #path('region_extractor/', include('region_extractor.urls')),
    path('hmm_creator/', include('hmm_creator.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]


urlpatterns += static(REGIONS_FILES_URL, document_root=REGIONS_FILES_ROOT)
urlpatterns += static(VITERBI_PATHS_FILES_URL, document_root=VITERBI_PATHS_FILES_ROOT)
urlpatterns += static(VITERBI_PATHS_FILES_URL, document_root=VITERBI_PATHS_FILES_ROOT)
urlpatterns += static(VITERBI_SEQ_COMPARISON_FILES_URL, document_root=VITERBI_SEQ_COMPARISON_FILES_ROOT)


