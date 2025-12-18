"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path

from . import views


urlpatterns = [

    path ('',views.home,name='home'),
    path ('about/',views.about,name='about'),
    path ('services/',views.services,name='services'),
    path ('contact/',views.contact,name='contact'),
    path('login/',views.login,name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('testator_register/',views.testator_register,name='testator_register'),

    path('uplaod_file/',views.uplaod_file,name='uplaod_file'),


    # -------------------------------------------------- LAWYER ----------------------------------------------------------------------------

    path('lawyer_home/',views.lawyer_home,name='lawyer_home'),

    path('lawyer_verify_testator/',views.lawyer_verify_testator,name='lawyer_verify_testator'),
    path('lawyer_approve_testator/<int:id>/', views.lawyer_approve_testator, name='lawyer_approve_testator'),
    path('lawyer_reject_testator/<int:id>/',views.lawyer_reject_testator,name='lawyer_reject_testator'),

    path('lawyer_view_testator/', views.lawyer_view_testator, name='lawyer_view_testator'),
    path('update-status/', views.update_status, name='update_status'),
    path('decrypt/<int:tid>/', views.decrypt_will, name='decrypt_will'),





    # -------------------------------------------------- TESTATOR ----------------------------------------------------------------------------

    path('testator_home/',views.testator_home,name='testator_home'),

    path('testator_add_will/',views.testator_add_will,name='testator_add_will'),





    # -------------------------------------------------- BENEFICIARY ----------------------------------------------------------------------------


    path('beneficiary_home/',views.beneficiary_home,name='beneficiary_home'),
    


    







]

from django.conf import settings
from django.conf.urls.static import static


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)