from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('profile/weight', views.weight_log_view, name='weight_log'),
    path('profile/weight/delete/<int:weight_id>', views.weight_log_delete, name='weight_log_delete'),

    path('food/list', views.food_list_view, name='food_list'),
    path('food/add', views.food_add_view, name='food_add'),
    path('food/foodlog', views.food_log_view, name='food_log'),
    path('food/foodlog/delete/<int:food_id>', views.food_log_delete, name='food_log_delete'),
    path('food/<str:food_id>', views.food_details_view, name='food_details'),

    path('categories', views.categories_view, name='categories_view'),
    path('categories/<str:category_name>', views.category_details_view, name='category_details_view'),

    path('water/', views.water_tracker_view, name='water_tracker'),
    path('water/log/', views.log_water, name='log_water'),  # Added slash
    path('water/settings/', views.water_settings_view, name='water_settings'),  # Added slash
    path('water/history/', views.water_history_view, name='water_history'),  # Added slash
    path('water/export/', views.export_water_data, name='export_water_data'),  # Added slash
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
