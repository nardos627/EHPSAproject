from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index,name='index'),
    path('course/', views.course, name='course'),
    path('allcourses/', views.allcourses, name='allcourses'),
    path('create_module/<int:course_id>/', views.create_module, name='create_module'),
    path('course/<int:course_id>/module/<int:module_id>/update/', views.update_module, name='update_module'),
    path('course/<int:course_id>/module/<int:module_id>/delete/', views.delete_module, name='delete_module'),
    path('<int:course_id>/modules/', views.course_modules, name='course_modules'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('courseviewpage/<int:course_id>/', views.courseviewpage, name='courseviewpage'),
    path('courseviewpage/<int:course_id>/video/<int:video_id>/', views.courseviewpagevideo, name='courseviewpagevideo'),
    path('courseviewpage/<int:course_id>/note/<int:note_id>/', views.courseviewpagenote, name='courseviewpagenote'),


    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('analytics/', views.analytics, name='analytic'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
