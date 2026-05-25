from django.urls import path
from .views import (
    login_view, register_view, dashboard_view, logout_view, admin_dashboard, api_overdue_complaints,
    staff_management, complaints, update_complaint, delete_complaint_admin, admin_zone_management,
    register_complaint, track_complaint, download_complaint_report, home, about_view, submit_contact,
    pricing_catalog_view, reports_view, contact_view, pay_fee, view_reports,
    schedule_public_view, admin_schedule_manage, maintenance_view, emergency_view, download_reports_view,
    submit_feedback, zone_management_view, vehicle_tracking_view,
    stripe_checkout, stripe_success, stripe_cancel,
    get_announcements, mark_announcement_read, mark_all_user_notifications_read, delete_all_user_notifications, delete_notification,
    get_zones, detect_zone,
    # Fleet Management
    api_vehicles_list, api_vehicle_history,
    fleet_admin_view, fleet_add_vehicle, fleet_edit_vehicle, fleet_delete_vehicle, fleet_upload_proof, assign_staff_area,
    # Service Scheduling
    service_admin_view, manage_service_categories, manage_bookings_admin, update_payment_settings,
    book_service_wizard, booking_stripe_checkout, booking_stripe_success,
    check_email_exists, admin_city_reports_view, payment_details_view, payment_admin_view,
    admin_wallet_view,
    impact_gallery_view, complaint_history_view, admin_complaint_history_view,
    wallet_view, wallet_deposit, wallet_deposit_success, link_stripe_account,
    admin_feedback_view, delete_feedback_admin, citizen_reviews_view,
    admin_notifications, notifications_view, service_history_view,
    admin_holiday_management, holiday_details_view, services_view,
    admin_contact_messages, admin_reply_contact, delete_contact_message,
    photo_gallery_view, admin_gallery_view, gallery_like_api, gallery_view_api,
    admin_gallery_list, admin_gallery_upload, admin_gallery_delete,
    admin_gallery_categories, admin_category_delete, api_gallery_toggle,
    get_admin_notifications, mark_admin_notifications_read, delete_admin_notification, mark_single_admin_notification_read,
    delete_all_admin_notifications
)

urlpatterns = [
    # User Authentication
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('api/check-email/', check_email_exists, name='check_email_exists'),

    # User Dashboard & Pages
    path('dashboard/', dashboard_view, name='dashboard'),
    path('catalog/', pricing_catalog_view, name='pricing_catalog'),
    path('home/', home, name='home'),
    path('about/', about_view, name='about'),
    path('services/', services_view, name='services'),
    path('contact/', contact_view, name='contact'),
    path('contact/submit/', submit_contact, name='submit_contact'),
    path('pay_fee/', pay_fee, name='pay_fee'),
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('citizen-reviews/', citizen_reviews_view, name='citizen_reviews'),


    # Announcements API & Views
    path('notifications/', notifications_view, name='notifications'),
    path('api/announcements/', get_announcements, name='get_announcements'),
    path('api/announcements/read/<int:pk>/', mark_announcement_read, name='mark_announcement_read'),
    path('api/announcements/read-all/', mark_all_user_notifications_read, name='mark_all_read'),
    path('api/announcements/delete/<int:pk>/', delete_notification, name='delete_notification'),
    path('api/announcements/delete-all/', delete_all_user_notifications, name='delete_all_notifications'),

    # Zones API
    path('api/zones/', get_zones, name='get_zones'),
    path('api/zones/detect/', detect_zone, name='detect_zone'),

    # Complaints
    path('complaint/', register_complaint, name='register_complaint'),
    path('track/', track_complaint, name='track'),
    path('track/<str:cid>/report/', download_complaint_report, name='download_complaint_report'),
    path('complaint-history/', complaint_history_view, name='complaint_history'),
    
    # Stripe Checkout Gateway
    path('stripe-checkout/', stripe_checkout, name='stripe_checkout'),
    path('stripe-success/', stripe_success, name='stripe_success'),
    path('stripe-cancel/', stripe_cancel, name='stripe_cancel'),

    # Reports
    path('reports/', reports_view, name='reports'),
    path('view_reports/', view_reports, name='view_reports'),
    path('reports/download/', download_reports_view, name='download_reports'),
    path('admin-city-reports/', admin_city_reports_view, name='admin_city_reports'),

    # Schedule / Maintenance / Emergency
    path('schedule/', schedule_public_view, name='schedule'),
    path('schedule/admin/', admin_schedule_manage, name='admin_schedule_manage'),
    path('maintenance/', maintenance_view, name='maintenance'),
    path('emergency/', emergency_view, name='emergency'),
    path('zone/', zone_management_view, name='zone_management'),
    path('vehicle/', vehicle_tracking_view, name='vehicle_tracking'),

    # Admin Module
    path('admin-dashboard/', admin_dashboard, name="admin_dashboard"),
    path('api/overdue-complaints/', api_overdue_complaints, name='api_overdue_complaints'),
    path('staff/', staff_management, name="staff"),
    path('complaints/', complaints, name="complaints"),
    path('admin-complaint-history/', admin_complaint_history_view, name="admin_complaint_history"),
    path('update-complaint/<int:id>/', update_complaint, name="update_complaint"),
    path('admin-zone/', admin_zone_management, name="admin_zone_management"),
    path('delete-complaint/<int:id>/', delete_complaint_admin, name="delete_complaint"),
    path('admin-wallet/', admin_wallet_view, name="admin_wallet"),

    # Fleet Monitoring System
    path('api/vehicles/', api_vehicles_list, name='api_vehicles'),
    path('api/vehicles/<int:pk>/history/', api_vehicle_history, name='api_vehicle_history'),
    path('fleet/admin/', fleet_admin_view, name='fleet_admin'),
    path('fleet/admin/add/', fleet_add_vehicle, name='fleet_add_vehicle'),
    path('fleet/admin/edit/<int:pk>/', fleet_edit_vehicle, name='fleet_edit_vehicle'),
    path('fleet/admin/delete/<int:pk>/', fleet_delete_vehicle, name='fleet_delete_vehicle'),
    path('fleet/admin/upload-proof/<int:pk>/', fleet_upload_proof, name='fleet_upload_proof'),
    path('fleet/admin/assign/', assign_staff_area, name='assign_staff_area'),

    # Service Scheduling & Booking
    path('service-admin/', service_admin_view, name='service_admin'),
    path('service-categories/manage/', manage_service_categories, name='manage_categories'),
    path('service-bookings/manage/', manage_bookings_admin, name='manage_bookings'),
    path('service-payment/settings/', update_payment_settings, name='update_payment_settings'),
    
    path('book-service/', book_service_wizard, name='book_service'),
    path('booking-stripe-checkout/', booking_stripe_checkout, name='booking_stripe_checkout'),
    path('booking-stripe-success/', booking_stripe_success, name='booking_stripe_success'),

    # Payments
    path('payment-details/', payment_details_view, name='payment_details'),
    path('admin-payments/', payment_admin_view, name='payment_admin'),
    path('impact-gallery/', impact_gallery_view, name='impact_gallery'),
    
    # Wallet
    path('wallet/', wallet_view, name='wallet'),
    path('wallet/link/', link_stripe_account, name='link_stripe_account'),
    path('wallet/deposit/', wallet_deposit, name='wallet_deposit'),
    path('wallet/deposit/success/', wallet_deposit_success, name='wallet_deposit_success'),
    
    # Citizen Feedback Admin
    path('admin-feedback/', admin_feedback_view, name='admin_feedback'),
    path('delete-feedback/<int:id>/', delete_feedback_admin, name='delete_feedback'),
    path('admin-notifications/', admin_notifications, name='admin_notifications'),
    path('admin-holiday/', admin_holiday_management, name='admin_holiday'),
    path('holiday-plan/<int:pk>/', holiday_details_view, name='holiday_details'),
    path('service-history/', service_history_view, name='service_history'),
    path('admin-contact/', admin_contact_messages, name='admin_contact_messages'),
    path('admin-contact/reply/<int:id>/', admin_reply_contact, name='admin_reply_contact'),
    path('admin-contact/delete/<int:id>/', delete_contact_message, name='delete_contact_message'),
    path('Photo-Gallery/', photo_gallery_view, name='gallery_page'),
    path('admin-Gallery/', admin_gallery_view, name='admin_gallery'),
    path('admin-Gallery/list/', admin_gallery_list, name='admin_gallery_list'),
    path('admin-Gallery/upload/', admin_gallery_upload, name='admin_gallery_upload'),
    path('admin-Gallery/edit/<int:pk>/', admin_gallery_upload, name='admin_gallery_edit'),
    path('admin-Gallery/delete/<int:pk>/', admin_gallery_delete, name='admin_gallery_delete'),
    path('admin-Gallery/categories/', admin_gallery_categories, name='admin_gallery_categories'),
    path('admin-Gallery/categories/delete/<int:pk>/', admin_category_delete, name='admin_category_delete'),
    path('api/gallery/toggle/', api_gallery_toggle, name='api_gallery_toggle'),
    path('api/gallery/like/', gallery_like_api, name='gallery_like_api'),
    path('api/gallery/view/', gallery_view_api, name='gallery_view_api'),
    path('api/admin-notifications/', get_admin_notifications, name='get_admin_notifications'),
    path('api/admin-notifications/read/', mark_admin_notifications_read, name='mark_admin_notifications_read'),
    path('admin-notifications/delete/<int:pk>/', delete_admin_notification, name='delete_admin_notification'),
    path('admin-notifications/read-single/<int:pk>/', mark_single_admin_notification_read, name='mark_single_admin_notification_read'),
    path('admin-notifications/delete-all/', delete_all_admin_notifications, name='delete_all_admin_notifications'),
]