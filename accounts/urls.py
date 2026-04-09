from django.urls import path
from .views import (
    login_view, register_view, dashboard_view, logout_view, admin_dashboard,
    staff_management, complaints, assign,
    register_complaint, track_complaint, home, about_view, submit_contact,
    services_view, reports_view, contact_view, pay_fee, view_reports,
    schedule_view, maintenance_view, emergency_view, download_reports_view
    
)

urlpatterns = [
    # User Authentication
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # User Dashboard & Pages
    path('dashboard/', dashboard_view, name='dashboard'),
    path('home/', home, name='home'),
    path('about/', about_view, name='about'),
    path('services/', services_view, name='services'),
    path('contact/', contact_view, name='contact'),
    path('contact/submit/', submit_contact, name='submit_contact'),
    path('pay_fee/', pay_fee, name='pay_fee'),

    # Complaints
    path('complaint/', register_complaint, name='register_complaint'),
    path('track/', track_complaint, name='track'),

    # Reports
    path('reports/', reports_view, name='reports'),
    path('view_reports/', view_reports, name='view_reports'),
    path('reports/download/', download_reports_view, name='download_reports'),

    # Schedule / Maintenance / Emergency
    path('schedule/', schedule_view, name='schedule'),
    path('maintenance/', maintenance_view, name='maintenance'),
    path('emergency/', emergency_view, name='emergency'),

    # Admin Module
    path('admin-dashboard/', admin_dashboard, name="admin_dashboard"),
    path('staff/', staff_management, name="staff"),
    path('complaints/', complaints, name="complaints"),
    path('assign/<int:id>/', assign, name="assign"),
    
]