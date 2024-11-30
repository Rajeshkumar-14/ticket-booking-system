from django.urls import path
from . import views

urlpatterns = [
    path("support-home/", views.support_home, name="support-home"),
    path("support-admin/", views.support_admin, name="support-admin"),
    path("load-messages/", views.load_messages, name="load-messages"),
    path('load-user-messages/<int:user_id>/', views.load_user_messages, name='load-user-messages'),
    path("clear-conversation/", views.clear_conversation, name="clear-conversation"),
     path('clear-admin-conversation/', views.clear_admin_conversation, name='clear-admin-conversation'),
]
