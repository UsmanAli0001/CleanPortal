from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import (
    Complaint, Feedback, GalleryLike, Vehicle, AdminNotification, Staff,
    Payment, ContactMessage, ServiceBooking, GalleryItem, Zone, Notification,
    ComplaintTimeline, Announcement
)
from allauth.account.signals import user_signed_up

from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

def notify_admin(type, message, link):
    """Helper to create admin notifications while preventing unread duplicates."""
    if not AdminNotification.objects.filter(type=type, message=message, is_read=False).exists():
        return AdminNotification.objects.create(type=type, message=message, link=link)
    return None

def send_aesthetic_email(subject, recipient_email, user_name, message_title, message_content, action_url=None, action_text=None):
    """Helper to send a premium-styled HTML email."""
    # Ensure absolute URL for action button
    final_action_url = action_url
    if action_url and action_url.startswith('/'):
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
        final_action_url = f"{site_url}{action_url}"

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
                <div class="welcome-title">Assalam o Alaikum, {user_name}!</div>
                <p>There is a new update regarding your interaction with <span class="brand-bold">Clean Pak Portal</span>.</p>
                
                <div class="info-box">
                    <span class="info-header">{message_title}</span>
                    <p style="margin: 0; font-size: 15px; color: #475569;">{message_content}</p>
                </div>

                <p>Thank you for helping us build a cleaner and smarter community.</p>
                
                {f'<div style="text-align: center;"><a href="{final_action_url}" class="btn">{action_text}</a></div>' if final_action_url else ''}
                
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
    
    print(f"DEBUG: Attempting to send email to {recipient_email} using {settings.DEFAULT_FROM_EMAIL}")
    try:
        send_mail(
            subject,
            message_content, # Plain text fallback
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
            html_message=html_content
        )
        print(f"SUCCESS: Email sent to {recipient_email}")
    except Exception as e:
        print(f"ERROR: SMTP delivery failed for {recipient_email}: {str(e)}")

@receiver(pre_save, sender=Complaint)
def capture_old_complaint_fields(sender, instance, **kwargs):
    try:
        if instance.pk:
            old_obj = Complaint.objects.get(pk=instance.pk)
            instance._old_status = old_obj.status
            instance._old_assigned_to = old_obj.assigned_to
            instance._old_priority = old_obj.priority
            instance._old_area = old_obj.area
            instance._old_proof_image = old_obj.proof_image.name if old_obj.proof_image else None
            instance._old_after_image = old_obj.after_image.name if old_obj.after_image else None
        else:
            instance._old_status = None
            instance._old_assigned_to = None
            instance._old_priority = None
            instance._old_area = None
            instance._old_proof_image = None
            instance._old_after_image = None
    except Complaint.DoesNotExist:
        instance._old_status = None
        instance._old_assigned_to = None
        instance._old_priority = None
        instance._old_area = None


@receiver(post_save, sender=Complaint)
def user_complaint_notification(sender, instance, created, **kwargs):
    recipient = instance.user or User.objects.filter(email=instance.email).first()
    
    if created:
        print(f"DEBUG: Complaint Creation Signal fired for {instance.complaint_id}")
        # Email notification for creation
        send_aesthetic_email(
            subject=f"Complaint Received: {instance.complaint_id}",
            recipient_email=instance.email,
            user_name=instance.name,
            message_title="Submission Confirmed",
            message_content=f"Your complaint {instance.complaint_id} ({instance.complaint_type}) in {instance.area} has been successfully recorded. Our team will verify it shortly. You can track the progress using your ID: {instance.complaint_id}.",
            action_url=reverse('track'),
            action_text="Track Progress"
        )
    else:
        print(f"DEBUG: Complaint Update Signal fired for {instance.complaint_id}")
        old_status = getattr(instance, '_old_status', None)
        old_assigned_to = getattr(instance, '_old_assigned_to', None)

        # CASE 1: Status Change
        if old_status != instance.status:
            print(f"DEBUG: Detected status change from {old_status} to {instance.status}")
            # In-app notification
            if recipient:
                notif = Notification(
                    user=recipient,
                    title=f"Complaint Status Update: {instance.complaint_id}",
                    message=f"Your complaint {instance.complaint_id} in {instance.area} has been updated to: {instance.status}.",
                    alert_type='success' if instance.status == 'Completed' else 'info'
                )
                notif._no_email = True
                notif.save()
            
            # Email notification
            send_aesthetic_email(
                subject=f"Update on Complaint {instance.complaint_id}",
                recipient_email=instance.email,
                user_name=instance.name,
                message_title=f"Status: {instance.status}",
                message_content=f"The status of your complaint {instance.complaint_id} ({instance.complaint_type}) in {instance.area} has been updated to {instance.status}.",
                action_url=reverse('track'),
                action_text="View Status"
            )
        
        # CASE 2: Staff Assignment Change
        if old_assigned_to != instance.assigned_to and instance.assigned_to:
            if recipient:
                notif = Notification(
                    user=recipient,
                    title=f"Staff Assigned: {instance.complaint_id}",
                    message=f"A staff member ({instance.assigned_to.name}) has been assigned to handle your complaint {instance.complaint_id}.",
                    alert_type='info'
                )
                notif._no_email = True
                notif.save()
            
            # Email notification
            send_aesthetic_email(
                subject=f"Team Assigned for Complaint {instance.complaint_id}",
                recipient_email=instance.email,
                user_name=instance.name,
                message_title="Technician Dispatched",
                message_content=f"Our team member {instance.assigned_to.name} ({instance.assigned_to.role}) has been assigned to your complaint {instance.complaint_id} in {instance.area}. They will be arriving shortly to resolve the issue."
            )

        # CASE 3: Proof of work / Completion Images uploaded
        elif (instance.proof_image and getattr(instance, '_old_proof_image', None) != instance.proof_image.name) or \
             (instance.after_image and getattr(instance, '_old_after_image', None) != instance.after_image.name):
            
            msg_title = "Work Completion Proof"
            msg_content = f"Great news! Our team has uploaded photographic proof of the resolution for your complaint {instance.complaint_id} in {instance.area}. You can now view the 'After' results in your dashboard."
            
            if recipient:
                notif = Notification(
                    user=recipient,
                    title=msg_title,
                    message=msg_content,
                    alert_type='success'
                )
                notif._no_email = True
                notif.save()

            send_aesthetic_email(
                subject=f"Proof of Resolution: {instance.complaint_id}",
                recipient_email=instance.email,
                user_name=instance.name,
                message_title=msg_title,
                message_content=msg_content,
                action_url=reverse('track'),
                action_text="View Proof"
            )

        # CASE 4: General Detail Update (Priority/Area)
        elif (getattr(instance, '_old_priority', None) != instance.priority or 
              getattr(instance, '_old_area', None) != instance.area):
            # Only send if status/staff didn't already trigger an email
            send_aesthetic_email(
                subject=f"Update on Complaint {instance.complaint_id}",
                recipient_email=instance.email,
                user_name=instance.name,
                message_title="Administrative Update",
                message_content=f"An administrator has updated the details of your complaint {instance.complaint_id}. The priority is now set to '{instance.priority}' and the area is confirmed as '{instance.area}'."
            )


@receiver(post_save, sender=Complaint)
def admin_complaint_notification(sender, instance, created, **kwargs):
    if created:
        notify_admin(
            type='complaint',
            message=f"🚨 New Complaint submitted! Type: {instance.complaint_type}. ID: {instance.complaint_id} from {instance.area}. Priority: {instance.priority}.",
            link=reverse('complaints')
        )
    else:
        # Deduplicate by only notifying if the status has actually changed
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            notify_admin(
                type='update',
                message=f"🔄 Complaint Update: {instance.complaint_id} status changed to {instance.status}.",
                link=reverse('complaints')
            )

@receiver(post_save, sender=Feedback)
def admin_feedback_notification(sender, instance, created, **kwargs):
    if created:
        notify_admin(
            type='feedback',
            message=f"⭐ New Citizen Review! {instance.rating} Stars received from {instance.user.username if instance.user else 'Anonymous'}.",
            link=reverse('admin_feedback')
        )

@receiver(post_save, sender=GalleryLike)
def admin_like_notification(sender, instance, created, **kwargs):
    if created:
        notify_admin(
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
    
    # Only notify on status change for updates to prevent duplicates
    if not created:
        old_status = getattr(instance, '_old_status', None)
        if old_status == instance.status:
            return

    notify_admin(
        type='update',
        message=f"🚚 Fleet Update: Vehicle {instance.vehicle_id} {action} to: {instance.status}.",
        link=reverse('fleet_admin')
    )

    if instance.current_complaint:
        old_status = getattr(instance, '_old_status', None)
        old_complaint = getattr(instance, '_old_complaint', None)
        complaint = instance.current_complaint
        recipient = complaint.user or User.objects.filter(email=complaint.email).first()

        # CASE 1: Newly assigned to a complaint
        if old_complaint != complaint:
            if recipient:
                notif = Notification(
                    user=recipient,
                    title=f"Vehicle Assigned: {instance.vehicle_id}",
                    message=f"Great news! A waste management vehicle ({instance.vehicle_id}) has been assigned to resolve your complaint {complaint.complaint_id}.",
                    alert_type='success'
                )
                notif._no_email = True
                notif.save()

                # Record assignment in Timeline
                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    status="Vehicle Assigned",
                    description=f"A specialized waste management vehicle ({instance.vehicle_id}) has been dispatched to your location."
                )
            
            # Email notification for Assignment
            send_aesthetic_email(
                subject=f"Vehicle Assigned for Complaint {complaint.complaint_id}",
                recipient_email=complaint.email,
                user_name=complaint.name,
                message_title="Fleet Dispatched",
                message_content=f"Great news! A specialized waste management vehicle ({instance.vehicle_id}) has been assigned to resolve your complaint {complaint.complaint_id} in {complaint.area}. Our team is now on the move to address the issue."
            )

        # CASE 2: Status changed for the already assigned complaint
        elif old_status and old_status != instance.status:
            if recipient:
                notif = Notification(
                    user=recipient,
                    title=f"Fleet Update: {instance.vehicle_id}",
                    message=f"The vehicle assigned to your complaint {complaint.complaint_id} is now {instance.status}.",
                    alert_type='info'
                )
                notif._no_email = True
                notif.save()

                # Update Complaint Timeline
                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    status="Fleet Activity",
                    description=f"Vehicle {instance.vehicle_id} status updated to: {instance.status}."
                )
            
            # Email notification for Status Update
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
    notify_admin(
        type='update',
        message=f"👥 Workforce Update: Staff {instance.name} has been {action}.",
        link=reverse('staff')
    )

@receiver(post_save, sender=Payment)
def user_payment_notification(sender, instance, created, **kwargs):
    if created:
        complaint = instance.complaint
        # notify admin
        notify_admin(
            type='update',
            message=f"💳 Revenue Alert! New payment of Rs. {instance.amount} received for {complaint.complaint_id}.",
            link=reverse('payment_admin')
        )
        # Notify User
        send_aesthetic_email(
            subject=f"Payment Received: {complaint.complaint_id}",
            recipient_email=complaint.email,
            user_name=complaint.name,
            message_title="Payment Confirmation",
            message_content=f"We have successfully received your payment of Rs. {instance.amount} for complaint {complaint.complaint_id}. Your request is now being processed by our operations team.",
            action_url=reverse('track'),
            action_text="Track Order"
        )

@receiver(post_save, sender=ContactMessage)
def admin_contact_notification(sender, instance, created, **kwargs):
    if created:
        notify_admin(
            type='complaint',
            message=f"📧 New Inquiry! {instance.name} sent a message regarding {instance.category}.",
            link=reverse('admin_contact_messages')
        )
        # Send receipt to user
        send_aesthetic_email(
            subject="We've received your inquiry",
            recipient_email=instance.email,
            user_name=instance.name,
            message_title="Inquiry Received",
            message_content=f"Thank you for reaching out to us regarding '{instance.category}'. Our support team has received your message and will get back to you shortly."
        )
    elif instance.is_replied and instance.reply:
        recipient = User.objects.filter(email=instance.email).first()
        if recipient:
            notif = Notification(
                user=recipient,
                title="New Reply to your Inquiry",
                message=f"An administrator has replied to your inquiry about '{instance.category}'.",
                alert_type='info'
            )
            notif._no_email = True
            notif.save()
        
        # Email notification
        send_aesthetic_email(
            subject=f"Reply to your inquiry: {instance.category}",
            recipient_email=instance.email,
            user_name=instance.name,
            message_title="Administrator Response",
            message_content=f"Regarding your query: \"{instance.message}\"\n\nResponse:\n{instance.reply}"
        )

@receiver(pre_save, sender=ServiceBooking)
def capture_old_booking_fields(sender, instance, **kwargs):
    """Captures old status and staff for bookings to detect changes."""
    try:
        if instance.pk:
            old_obj = ServiceBooking.objects.get(pk=instance.pk)
            instance._old_status = old_obj.status
            instance._old_assigned_staff = old_obj.assigned_staff
        else:
            instance._old_status = None
            instance._old_assigned_staff = None
    except ServiceBooking.DoesNotExist:
        instance._old_status = None
        instance._old_assigned_staff = None

@receiver(post_save, sender=ServiceBooking)
def user_booking_notification(sender, instance, created, **kwargs):
    """Notifies the user about booking creation and subsequent updates."""
    recipient = instance.user
    if created:
        # Admin Notification
        notify_admin(
            type='update',
            message=f"📅 New Booking! {instance.service.name} scheduled by {instance.user.username}.",
            link=reverse('manage_bookings')
        )
        # User Confirmation Email
        send_aesthetic_email(
            subject=f"Booking Confirmed: {instance.service.name}",
            recipient_email=recipient.email,
            user_name=recipient.first_name or recipient.username,
            message_title="Service Scheduled",
            message_content=f"Your booking for {instance.service.name} has been confirmed for {instance.scheduled_date}. Our team will arrive at your address: {instance.address}.",
            action_url=reverse('dashboard'),
            action_text="View Dashboard"
        )
    else:
        print(f"DEBUG: ServiceBooking Update Signal fired for booking {instance.id}")
        old_status = getattr(instance, '_old_status', None)
        old_staff = getattr(instance, '_old_assigned_staff', None)

        # CASE 1: Status Change
        if old_status != instance.status:
            print(f"DEBUG: Detected booking status change from {old_status} to {instance.status}")
            if recipient:
                notif = Notification(
                    user=recipient,
                    title=f"Booking Update: {instance.service.name}",
                    message=f"Your booking for {instance.service.name} on {instance.scheduled_date} has been updated to: {instance.status}.",
                    alert_type='info'
                )
                notif._no_email = True
                notif.save()
            
            # Email notification
            send_aesthetic_email(
                subject=f"Update on Service Booking: {instance.service.name}",
                recipient_email=recipient.email,
                user_name=recipient.first_name or recipient.username,
                message_title=f"Booking Status: {instance.status}",
                message_content=f"Your scheduled service for {instance.service.name} on {instance.scheduled_date} has been updated to '{instance.status}' by our administration."
            )

        # CASE 2: Staff Assignment
        if old_staff != instance.assigned_staff and instance.assigned_staff:
            if recipient:
                notif = Notification(
                    user=recipient,
                    title=f"Team Assigned: {instance.service.name}",
                    message=f"Technician {instance.assigned_staff.name} has been assigned to your service booking for {instance.service.name}.",
                    alert_type='success'
                )
                notif._no_email = True
                notif.save()
            
            # Email notification
            send_aesthetic_email(
                subject=f"Technician Assigned for your Service",
                recipient_email=recipient.email,
                user_name=recipient.first_name or recipient.username,
                message_title="Team Member Dispatched",
                message_content=f"Our professional technician, {instance.assigned_staff.name}, has been assigned to fulfill your booking for {instance.service.name} on {instance.scheduled_date}. They will reach your address shortly."
            )

@receiver(pre_save, sender=GalleryItem)
def capture_old_gallery_fields(sender, instance, **kwargs):
    """Captures old complaint to detect changes in post_save."""
    try:
        if instance.pk:
            old_obj = GalleryItem.objects.get(pk=instance.pk)
            instance._old_complaint = old_obj.complaint
        else:
            instance._old_complaint = None
    except GalleryItem.DoesNotExist:
        instance._old_complaint = None

@receiver(post_save, sender=GalleryItem)
def gallery_item_notifications(sender, instance, created, **kwargs):
    """Notifies admins and relevant users about gallery showcase updates."""
    action = "published" if created else "updated"
    
    # 1. Admin Notification
    notify_admin(
        type='update',
        message=f"Gallery item '{instance.title}' has been {action}.",
        link=reverse('admin_gallery_list')
    )

    # 2. User Notification (If linked to a complaint)
    if instance.complaint:
        complaint = instance.complaint
        recipient = complaint.user or User.objects.filter(email=complaint.email).first()
        
        # Determine if we should notify the user (always on create/update if linked)
        if recipient:
            msg_title = f"Gallery Update: {complaint.complaint_id}"
            msg_content = f"The transformation showcase for your complaint {complaint.complaint_id} in {complaint.area} has been {action} in our public gallery. We are proud to share this positive impact with the community!"
            
            notif = Notification(
                user=recipient,
                title=msg_title,
                message=msg_content,
                alert_type='success'
            )
            notif._no_email = True
            notif.save()
            
            # Email notification
            send_aesthetic_email(
                subject=f"Gallery Update for {complaint.complaint_id}",
                recipient_email=complaint.email,
                user_name=complaint.name,
                message_title="Transformation Showcase",
                message_content=msg_content,
                action_url=reverse('impact_gallery'),
                action_text="View Gallery"
            )

@receiver(post_save, sender=Zone)
def admin_zone_notification(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    notify_admin(
        type='update',
        message=f"Zone '{instance.name}' has been {action}.",
        link=reverse('admin_zone_management')
    )

@receiver(post_save, sender=Announcement)
def user_announcement_notification(sender, instance, created, **kwargs):
    """Sends a system-wide email for new broadcasts."""
    if created and instance.is_active:
        users = User.objects.filter(is_active=True)
        for user in users:
            if user.email:
                send_aesthetic_email(
                    subject=f"System Update: {instance.title}",
                    recipient_email=user.email,
                    user_name=user.first_name or user.username,
                    message_title="Broadcast Announcement",
                    message_content=instance.message,
                    action_url=reverse('dashboard'),
                    action_text="View Dashboard"
                )

@receiver(post_save, sender=Notification)
def user_direct_notification(sender, instance, created, **kwargs):
    """Ensures manual notifications sent by admins also go to email."""
    if created and instance.user and instance.user.email:
        # If the notification has _no_email flag, skip it (used by automated signals)
        if getattr(instance, '_no_email', False):
            print(f"DEBUG: Skipping email for automated notification: {instance.title}")
            return

        print(f"DEBUG: Processing personal message email for: {instance.user.email}")
        send_aesthetic_email(
            subject=f"New Notification: {instance.title}",
            recipient_email=instance.user.email,
            user_name=instance.user.first_name or instance.user.username,
            message_title=instance.title,
            message_content=instance.message,
            action_url=reverse('notifications'),
            action_text="View All"
        )

@receiver(user_signed_up)
def allauth_welcome_email(request, user, **kwargs):
    """Sends a premium welcome email when a user signs up via Google or Social providers."""
    if user.email:
        send_aesthetic_email(
            subject="Welcome to Clean Pak Portal",
            recipient_email=user.email,
            user_name=user.first_name or user.username,
            message_title="Registration Successful! 🎉",
            message_content="Welcome to Clean Pak Portal! Your account has been successfully created. You can now submit complaints, track progress in real-time, and help us build a cleaner community.",
            action_url=reverse('dashboard'),
            action_text="Get Started"
        )
