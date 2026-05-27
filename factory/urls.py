from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register_view, name='register'),   # use register_view (with logic)
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path("add_factoryprofile/", views.add_factoryprofile, name="add_factoryprofile"),
    path('factory-dashboard/', views.factory_dashboard, name='factory_dashboard'),
    path("add_asset/", views.add_asset, name="add_asset"),
    path('add_usage/', views.add_usage, name='add_usage'),
    # path('dashboard/', views.factory_dashboard, name='factory_dashboard'),
    path('reports/', views.reports_page, name='reports'),    # HTML page
    path('api/reports/', views.generate_report, name='reports-api'), # returns JSON
    #path('notifications/', views.notifications_page, name='notifications'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/delete/', views.delete_notification, name='delete_notification'),
    #path('notifications/mark-read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('factory/<int:factory_id>/profile/', views.factory_profile_view, name='factory_profile'),
    #path('add-factory-profile/', views.add_factoryprofile, name='add_factoryprofile'),
    path('change-password/', views.change_password, name='change_password'),
    path('request-closure/', views.request_account_closure, name='request_closure'),
    path('deactivate-account/', views.deactivate_account, name='deactivate_account'),
    path('account-management/', views.account_management_view, name='account_management'),
    path('factory-selection/', views.select_factory_view, name='select_factory'),  # <-- make sure this exists
    path('set-active-factory/', views.set_active_factory, name='set_active_factory'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    #path('admin/manage-factories/', views.manage_factories, name='manage_factories'),
    path('admin-dashboard/manage-factories/', views.manage_factories, name='manage_factories'),
    path('admin/delete-factory/<int:factory_id>/', views.delete_factory, name='delete_factory'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    #path('admin/reports/csv/', views.admin_reports_csv, name='admin_reports_csv'),
    path('admin-reports-pdf/', views.admin_reports_pdf, name='admin_reports_pdf'),
    path('admin/announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin/announcements/create/', views.create_announcement, name='create_announcement'),
    path('admin/notifications/', views.admin_notifications_view, name='admin_notifications'),
    path('admin/profile/', views.admin_profile_view, name='admin_profile'),
    #path('admin-profile/', views.admin_profile_view, name='admin_profile'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-delete-notification/<int:notif_id>/', views.admin_delete_notification, name='admin_delete_notification'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
   # path('reset-password/', views.reset_password, name='reset_password'),
    #path('reset-password/<str:email>/', views.reset_password, name='reset_password'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),

    #path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    #path('admin/manage-factories/', views.manage_factories, name='manage_factories'),
    #path('admin/delete-factory/<int:factory_id>/', views.delete_factory, name='delete_factory'),
   # path('admin/reports/', views.admin_reports, name='admin_reports'),
    #path('/reports/csv/', views.admin_reports_csv, name='admin_reports_csv'),
    #path('admin/notifications/', views.admin_notifications_view, name='admin_notifications'),
    #path('admin-profile/', views.admin_profile_view, name='admin_profile'),
    #path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('forgot-password/', 
         auth_views.PasswordResetView.as_view(
             template_name='factory/forgot-password.html',
             email_template_name='factory/password_reset_email.txt',
             subject_template_name='factory/password_reset_subject.txt',
             success_url='/forgot-password/done/'
         ), 
         name='forgot_password'),

    path('forgot-password/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='factory/password_reset_done.html'
         ), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='factory/password_reset_confirm.html',
             success_url='/reset/done/'
         ), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='factory/password_reset_complete.html'
         ), 
         name='password_reset_complete'),


]

