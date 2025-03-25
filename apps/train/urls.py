from django.urls import path

from . import views

app_name = "train"

urlpatterns = [
    path('train-home/', views.train_home, name='train-home'),
    path(
        'check-train-availability/',
        views.check_train_availability,
        name='check-train-availability',
    ),
    path('train-reservation/<int:id>/', views.train_reservation, name='train-reservation'),
    path('save-train-reservation/', views.save_train_reservation, name='save-train-reservation'),
    path(
        'cancel-train-reservation/',
        views.cancel_train_reservation,
        name='cancel-train-reservation',
    ),
    path('cancel-train-trip/', views.cancel_train_trip, name='cancel-train-trip'),
]
