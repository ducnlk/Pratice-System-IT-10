"""
URL configuration for demoform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
    path('index', views.index, name="index"),
    path('', views.index, name="index"),
    path('_classes', views._classes,name='_classes'),
    path('exam', views.exam, name = 'exam'),
    path('blank', views.blank,name='blank'),
    path('practice', views.practice, name = 'practice'),
    path('forgot_password', views.forgot_password,name='forgot_password'),
    path('register', views.register, name = 'register'),
    path('utilities_animation', views.utilities_animation,name='utilities_animation'),
    path('utilities_color', views.utilities_color, name = 'utilities_color'),
    path('utilities_other', views.utilities_other,name='utilities_other'),
    path('detail_exam/<str:exam_id>/', views.detail_exam,name='detail_exam'),
    path('_404', views._404,name='_404'),
    path('login', views.class_login.as_view(),name='login'),
    path('detail_class/<str:classroom_id>/', views.detail_class,name='detail_class'),
    path('add_practice', views.add_practice,name='add_practice'),
    path('add_exam', views.add_exam,name='add_exam'),
    path('detail_practice/<str:test_id>/', views.detail_practice,name='detail_practice'),
    path('do/<str:test_id>', views.do,name='do'),
    path('save_exam_data/', views.save_exam_data, name='save_exam_data'),
    path('save_a_practice/', views.save_a_practice, name='save_a_practice'),
    path('reload_results/', views.reload_results, name='reload_results'),
    path('result_test', views.result_test,name='result_test'),
    path('logout/', views.user_logout, name='logout'),
    path('reload_classroom_results/', views.reload_classroom_results, name='reload_classroom_results'),
]
