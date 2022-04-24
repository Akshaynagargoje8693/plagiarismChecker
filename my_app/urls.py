from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
urlpatterns = [
    path('',views.home),
    path('login/',views.login),
    path('login/logic/',views.loginLogic),
    path('register/',views.register),
    path('register/logic/',views.registerlogic),
    path('plagiarism/',views.postUpload),
    path('plagiarism/check',views.plagiarismRender),
    path('uploadFiles/',views.uploadMultipleFilesRender),
    path('uploadFiles/logic',views.uploadMultipleFiles),
    path('addfile/',views.addFile),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
