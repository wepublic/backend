"""wepublic_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from wp_core.views import TagViewSet, QuestionsViewSet
from wp_core.views_answers import AnswerViewSet
from users.views import UserViewSet
from wp_news.views import NewsEntryViewSet
from wp_newsletter.views import NewsLetterAddressViewSet
from wp_party.views import PartyViewSet

from rest_framework_swagger.views import get_swagger_view


router = DefaultRouter()
router.register(r'Tags', TagViewSet)
router.register(r'Questions', QuestionsViewSet)
router.register(r'Answers', AnswerViewSet)
router.register(r'Users', UserViewSet)
router.register(r'News', NewsEntryViewSet)
router.register(r'Newsletter', NewsLetterAddressViewSet)
router.register(r'Parties', PartyViewSet)
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^v1/', include(router.urls)),
    url(r'^docs/', csrf_exempt(get_swagger_view(title='Wepublic API'))),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(
            settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT)
