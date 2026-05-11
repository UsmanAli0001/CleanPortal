from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    Complaint, Feedback, GalleryLike, Vehicle, AdminNotification, Staff,
    Payment, ContactMessage, ServiceBooking, GalleryItem, Zone, Notification,
    ComplaintTimeline
)


from django.urls import reverse

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

def send_aesthetic_email(subject, recipient_email, user_name, message_title, message_content, action_url=None, action_text=None):
    """Helper to send a premium-styled HTML email."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .email-container {{ font-family: 'Outfit', 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 24px; overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #1d4ed8, #3b82f6); color: white; padding: 40px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -1px; }}
            .content {{ padding: 40px; background-color: #ffffff; }}
            .welcome-title {{ font-size: 22px; color: #1e3a8a; font-weight: 800; margin-bottom: 20px; }}
            .info-box {{ background-color: #f8fafc; border-radius: 20px; padding: 25px; margin: 30px 0; border: 1px solid #e2e8f0; }}
            .info-header {{ font-size: 16px; font-weight: 800; color: #3b82f6; margin-bottom: 10px; display: block; text-transform: uppercase; }}
            .footer {{ background-color: #f1f5f9; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0; }}
            .brand-bold {{ color: #1d4ed8; font-weight: 900; }}
            .btn {{ display: inline-block; padding: 14px 30px; background: #1d4ed8; color: white !important; text-decoration: none; border-radius: 12px; font-weight: 700; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Clean Pak Portal</h1>
            </div>
            <div class="content">
                <div class="welcome-title">Hello, {user_name}!</div>
                <p>There is a new update regarding your interaction with <span class="brand-bold">Clean Pak Portal</span>.</p>
                
                <div class="info-box">
                    <span class="info-header">{message_title}</span>
                    <p style="margin: 0; font-size: 15px; color: #475569;">{message_content}</p>
                </div>

                <p>Thank you for helping us build a cleaner and smarter community.</p>
                
                {f'<div style="text-align: center;"><a href="{action_url}" class="btn">{action_text}</a></div>' if action_url else ''}
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #eff6ff;">
                    <p><b>Best Regards,</b><br><span class="brand-bold">Clean Pak Portal Team</span></p>
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2026 <b>Clean Pak Portal</b>. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_mail(
        subject,
        message_content, # Plain text fallback
        settings.EMAIL_HOST_USER,
        [recipient_email],
        fail_silently=True,
        html_message=html_content
    )
from django.db.models.signals import pre_save

@receiver(pre_save, sender=Complaint)
def capture_old_complaint_status(sender, instance, **kwargs):
    try:
        if instance.pk:
            instance._old_status = Complaint.objects.get(pk=instance.pk).status
        else:
            instance._old_status = None
    except Complaint.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Complaint)
def user_complaint_notification(sender, instance, created, **kwargs):
    if not created:
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            # In-app notification
            recipient = instance.user or User.objects.filter(email=instance.email).first()
            if recipient:
                Notification.objects.create(
                    user=recipient,
                    title=f"Complaint Status Update: {instance.complaint_id}",
                    message=f"Your complaint {instance.complaint_id} in {instance.area} has been updated to: {instance.status}.",
                    alert_type='success' if instance.status == 'Completed' else 'info'
                )
            
            # Email notification
            send_aesthetic_email(
                subject=f"Update on Complaint {instance.complaint_id}",
                recipient_email=instance.email,
                user_name=instance.name,
                message_title=f"Status: {instance.status}",
                message_content=f"The status of your complaint {instance.complaint_id} ({instance.complaint_type}) in {instance.area} has been updated to {instance.status}."
            )


@receiver(post_save, sender=Complaint)
def admin_complaint_notification(sender, instance, created, **kwargs):

    if created:
        AdminNotification.objects.create(
            type='complaint',
            message=f"🚨 New Complaint submitted! ID: {instance.complaint_id} from {instance.area}. Priority: {instance.priority}.",
            link=reverse('complaints')
        )
    else:
        AdminNotification.objects.create(
            type='update',
            message=f"🔄 Complaint Update: {instance.complaint_id} status changed to {instance.status}.",
            link=reverse('complaints')
        )

@receiver(post_save, sender=Feedback)
def admin_feedback_notification(sender, instance, created, **kwargs):
    if created:
        AdminNotification.objects.create(
            type='feedback',
            message=f"⭐ New Citizen Review! {instance.rating} Stars received from {instance.user.username if instance.user else 'Anonymous'}.",
            link=reverse('admin_feedback')
        )

@receiver(post_save, sender=GalleryLike)
def admin_like_notification(sender, instance, created, **kwargs):
    if created:
        AdminNotification.objects.create(
            type='like',
            message=f"❤️ Gallery Engagement! A user liked the project: {instance.gallery_item.title}.",
            link=reverse('admin_gallery_list')
        )

@receiver(pre_save, sender=Vehicle)
def capture_old_vehicle_fields(sender, instance, **kwargs):
    """Captures old status and complaint to detect changes in post_save."""
    try:
        if instance.pk:
            old_obj = Vehicle.objects.get(pk=instance.pk)
            instance._old_status = old_obj.status
            instance._old_complaint = old_obj.current_complaint
        else:
            instance._old_status = None
            instance._old_complaint = None
    except Vehicle.DoesNotExist:
        instance._old_status = None
        instance._old_complaint = None

@receiver(post_save, sender=Vehicle)
def admin_vehicle_notification(sender, instance, created, **kwargs):

    action = "onboarded" if created else "status updated"
    AdminNotification.objects.create(
        type='update',
        message=f"🚚 Fleet Update: Vehicle {instance.vehicle_id} {action} to: {instance.status}.",
        link=reverse('fleet_admin')
    )

    if not created and instance.current_complaint:
        old_status = getattr(instance, '_old_status', None)
        old_complaint = getattr(instance, '_old_complaint', None)
        complaint = instance.current_complaint
        recipient = complaint.user or User.objects.filter(email=complaint.email).first()

        # CASE 1: Newly assigned to a complaint
        if old_complaint != complaint:
            if recipient:
                Notification.objects.create(
                    user=recipient,
                    title=f"Vehicle Assigned: {instance.vehicle_id}",
                    message=f"Great news! A waste management vehicle ({instance.vehicle_id}) has been assigned to resolve your complaint {complaint.complaint_id}.",
                    alert_type='success'
                )

                # Record assignment in Timeline
                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    status="Vehicle Assigned",
                    description=f"A specialized waste management vehicle ({instance.vehicle_id}) has been dispatched to your location."
                )

        # CASE 2: Status changed for the already assigned complaint
        elif old_status and old_status != instance.status:
            if recipient:
                Notification.objects.create(
                    user=recipient,
                    title=f"Fleet Update: {instance.vehicle_id}",
                    message=f"The vehicle assigned to your complaint {complaint.complaint_id} is now {instance.status}.",
                    alert_type='info'
                )

                # Update Complaint Timeline
                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    status="Fleet Activity",
                    description=f"Vehicle {instance.vehicle_id} status updated to: {instance.status}."
                )
            
            # Email notification
            send_aesthetic_email(
                subject=f"Fleet Update for Complaint {complaint.complaint_id}",
                recipient_email=complaint.email,
                user_name=complaint.name,
                message_title=f"Vehicle Status: {instance.status}",
                message_content=f"The waste management vehicle ({instance.vehicle_id}) assigned to your complaint {complaint.complaint_id} is now {instance.status}."
            )



@receiver(post_save, sender=Staff)
def admin_staff_notification(sender, instance, created, **kwargs):
    action = "onboarded" if created else "profile updated"
    AdminNotification.objects.create(
        type='update',
        message=f"👥 Workforce Update: Staff {instance.name} has been {action}.",
        link=reverse('staff')
    )

@receiver(post_save, sender=Payment)
def admin_payment_notification(sender, instance, created, **kwargs):
    if created:
        AdminNotification.objects.create(
            type='update',
            message=f"💳 Revenue Alert! New payment of Rs. {instance.amount} received for {instance.complaint.complaint_id}.",
            link=reverse('payment_admin')
        )

@receiver(post_save, sender=ContactMessage)
def admin_contact_notification(sender, instance, created, **kwargs):
    if created:
        AdminNotification.objects.create(
            type='complaint',
            message=f"📧 New Inquiry! {instance.name} sent a message regarding {instance.category}.",
            link=reverse('admin_contact_messages')
        )
    elif instance.is_replied and instance.reply:
        # Check if the notification was already sent (optional, but good practice)
        # For simplicity, we just create it. The user might get multiple if admin edits reply.
        
        recipient = User.objects.filter(email=instance.email).first()
        if recipient:
            Notification.objects.create(
                user=recipient,
                title="New Reply to your Inquiry",
                message=f"An administrator has replied to your inquiry about '{instance.category}'.",
                alert_type='info'
            )
        
        # Email notification
        send_aesthetic_email(
            subject=f"Reply to your inquiry: {instance.category}",
            recipient_email=instance.email,
            user_name=instance.name,
            message_title="Administrator Response",
            message_content=f"Regarding your query: \"{instance.message}\"\n\nResponse:\n{instance.reply}"
        )


@receiver(post_save, sender=ServiceBooking)
def admin_booking_notification(sender, instance, created, **kwargs):
    if created:
        AdminNotification.objects.create(
            type='update',
            message=f"📅 New Booking! {instance.service.name} scheduled by {instance.user.username}.",
            link=reverse('manage_bookings')
        )

@receiver(post_save, sender=GalleryItem)
def admin_gallery_item_notification(sender, instance, created, **kwargs):
    action = "published" if created else "updated"
    AdminNotification.objects.create(
        type='update',
        message=f"Gallery item '{instance.title}' has been {action}.",
        link=reverse('admin_gallery_list')
    )

@receiver(post_save, sender=Zone)
def admin_zone_notification(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    AdminNotification.objects.create(
        type='update',
        message=f"Zone '{instance.name}' has been {action}.",
        link=reverse('admin_zone_management')
    )
