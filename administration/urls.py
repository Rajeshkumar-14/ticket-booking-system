from django.urls import path

from . import views

__project_by__ = "RajeshKumar"

urlpatterns = [
    path("", views.administration, name="administration-home"),
    # BUS
    path("bus-index/", views.bus_index, name="bus-index"),
    path("create-bus/", views.create_bus, name="create-bus"),
    path("edit-bus/<int:bus_id>/", views.edit_bus, name="edit-bus"),
    path("update-bus/<int:bus_id>/", views.update_bus, name="update-bus"),
    path("bus-details/<int:bus_id>/", views.bus_details, name="bus-details"),
    path("delete-bus/", views.delete_bus, name="delete-bus"),
    path("bus-history/", views.bus_history, name="bus-history"),
    path(
        "admin-bus-travel-history/",
        views.bus_travel_history,
        name="admin-bus-travel-history",
    ),
    # FLIGHT
    path("flight-index/", views.flight_index, name="flight-index"),
    path("create-flight/", views.create_flight, name="create-flight"),
    path("edit-flight/<int:flight_id>/", views.edit_flight, name="edit-flight"),
    path("update-flight/<int:flight_id>/", views.update_flight, name="update-flight"),
    path("flight-details/<int:flight_id>/", views.flight_details, name="flight-details"),
    path("delete-flight/", views.delete_flight, name="delete-flight"),
    path("flight-history/", views.flight_history, name="flight-history"),
    path(
        "admin-flight-travel-history/",
        views.flight_travel_history,
        name="admin-flight-travel-history",
    ),
    # TRAIN
    path("train-index/", views.train_index, name="train-index"),
    path("create-train/", views.create_train, name="create-train"),
    path("edit-train/<int:train_id>/", views.edit_train, name="edit-train"),
    path("update-train/<int:train_id>/", views.update_train, name="update-train"),
    path("train-details/<int:train_id>/", views.train_details, name="train-details"),
    path("delete-train/", views.delete_train, name="delete-train"),
    path("train-history/", views.train_history, name="train-history"),
    path(
        "admin-train-travel-history/",
        views.train_travel_history,
        name="admin-train-travel-history",
    ),
]
