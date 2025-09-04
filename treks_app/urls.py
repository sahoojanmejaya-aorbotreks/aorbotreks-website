from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
     path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('user-agreement/', views.user_agreement, name='user_agreement'),
    path('safety/', views.safety, name='safety'),
    
    # Blog pages
    path('blogs/', views.blogs, name='blogs'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Trek pages
    path('treks/', views.treks, name='treks'),
    path('treks/<slug:slug>/', views.trek_detail, name='trek_detail'),
    
    # API endpoints
    path('api/contact/', views.contact_submit, name='contact_submit'),
]
