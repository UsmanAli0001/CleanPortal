from django.contrib import admin
from .models import (
    Profile, Complaint, ComplaintTimeline, Staff,
    Payment, Announcement, RouteAlert, Feedback,
    CleaningSchedule, AnnouncementRead, Zone,
    Vehicle, VehicleLocation, ComplaintPricingConfig
)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'assigned_staff', 'complaint_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name',)
    change_form_template = 'admin/accounts/zone/change_form.html'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'is_active', 'created_at')
    list_filter = ('alert_type', 'is_active', 'created_at')
    search_fields = ('title', 'message')
    list_editable = ('is_active',)

@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'announcement', 'read_at')
    list_filter = ('read_at',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'complaint_type', 'area', 'status', 'created_at')
    list_filter = ('status', 'area', 'priority')
    search_fields = ('complaint_id', 'name', 'description')

admin.site.register(ComplaintTimeline)
admin.site.register(Staff)
admin.site.register(Payment)
admin.site.register(RouteAlert)
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'stars_display', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')

    def stars_display(self, obj):
        return "⭐" * obj.rating
    stars_display.short_description = 'Rating'
admin.site.register(CleaningSchedule)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_id', 'vehicle_type', 'driver_name', 'assigned_zone', 'status', 'is_active', 'created_at')
    list_filter = ('vehicle_type', 'status', 'is_active')
    search_fields = ('vehicle_id', 'driver_name', 'assigned_zone', 'plate_number')
    list_editable = ('status', 'is_active')

@admin.register(VehicleLocation)
class VehicleLocationAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'latitude', 'longitude', 'speed', 'timestamp')
    list_filter = ('vehicle', 'timestamp')
    ordering = ('-timestamp',)

@admin.register(ComplaintPricingConfig)
class ComplaintPricingConfigAdmin(admin.ModelAdmin):
    list_display = ('distance_range', 'base_price', 'urgent_price', 'is_active')
    list_editable = ('base_price', 'urgent_price', 'is_active')