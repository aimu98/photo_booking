
from django.urls import path
from . import views
from photo_booking_app import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'), 
    path('reservation/', views.reservation_view, name='reservation'),
    path('reservation/done/', views.reservation_done, name='reservation_done'),
    path('api/available-times/', views.get_available_times, name='get_available_times'),
    path('api/available-dates/', views.get_available_dates, name='get_available_dates'),
    path('add_available_slot/', views.add_available_slot, name='add_available_slot'),
    path('available_slots/', views.available_slots_view, name='available_slots'),
    path('reservation_history/', views.reservation_history, name='reservation_history'),
    path('reservation/<int:reservation_id>/edit/', views.edit_reservation, name='edit_reservation'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('mypage/', views.mypage, name='mypage'),
    path('admin/reservations/', views.admin_reservation_dashboard, name='admin_reservation_dashboard'),
    path('admin/reservations/<int:user_id>/', views.admin_reservation_list, name='admin_reservation_list_by_user'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('logout/done/', views.logout_done, name='logout_done'),
    path('password_reset/', views.password_reset_request, name='password_reset'), 
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'), 
    path('password_reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'), 
    path('password_reset/complete/', views.password_reset_complete, name='password_reset_complete'), 
    
]
