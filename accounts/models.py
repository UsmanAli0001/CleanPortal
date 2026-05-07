from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    email_verified = models.BooleanField(
        default=False
    )

    def __str__(self):

        return self.user.username

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a new User is created (e.g. via Google)."""
    if created:
        Profile.objects.get_or_create(user=instance)

class Complaint(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]

    PRIORITY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent')
    ]

    complaint_id = models.CharField(
        max_length=50,
        unique=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='complaints'
    )
    name = models.CharField(
        max_length=100
    )
    email = models.EmailField()


    complaint_type = models.CharField(
        max_length=50
    )

    area = models.CharField(
        max_length=100
    )

    description = models.TextField()

    # ADD THESE ↓↓↓

    image = models.ImageField(

        upload_to='complaints/images/',

        null=True,

        blank=True

    )

    video = models.FileField(

        upload_to='complaints/videos/',

        null=True,

        blank=True

    )

    # OPTIONAL (since you capture map location)

    latitude = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    longitude = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Normal'
    )

    payment_status = models.BooleanField(
        default=False
    )

    after_image = models.ImageField(
        upload_to='complaints/after_images/',
        null=True,
        blank=True,
        help_text="Proof of completion by staff"
    )

    proof_image = models.ImageField(
        upload_to='complaints/proof_images/',
        null=True,
        blank=True,
        help_text="Official completion proof (Admin)"
    )

    proof_video = models.FileField(
        upload_to='complaints/proof_videos/',
        null=True,
        blank=True,
        help_text="Official completion proof (Admin)"
    )

    assigned_to = models.ForeignKey(
        'Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='Pending'

    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    fee_tier = models.ForeignKey(
        'ComplaintPricingConfig',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return self.complaint_id

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            last = Complaint.objects.count()
            self.complaint_id = "GRT-2026-" + str(last + 1).zfill(4)
        super().save(*args, **kwargs)

@receiver(post_save, sender=Complaint)
def track_complaint_status(sender, instance, created, **kwargs):
    """Automatically create a timeline entry when a complaint is created or its status changes."""
    # Only create if it doesn't exist for this status yet
    if not ComplaintTimeline.objects.filter(complaint=instance, status=instance.status).exists():
        description = f"Complaint status updated to {instance.status}."
        if created:
            description = "Complaint submitted successfully and payment verified."
        
        ComplaintTimeline.objects.create(
            complaint=instance,
            status=instance.status,
            description=description
        )

class ComplaintTimeline(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='timeline')
    status = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.complaint_id} - {self.status}"


class Notification(models.Model):
    ALERT_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=200, default="System Update")
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username if self.user else 'General'}"
from django.contrib.auth.models import User

class Staff(models.Model):

    ROLE = (

        ('Worker','Worker'),

        ('Driver','Driver'),

        ('Supervisor','Supervisor')

    )

    name=models.CharField(max_length=100)

    phone=models.CharField(max_length=20)

    role=models.CharField(max_length=50,choices=ROLE)

    area=models.CharField(max_length=100)

    age = models.IntegerField(null=True, blank=True)

    duties = models.CharField(max_length=200, blank=True, help_text="e.g., Sweeper, Garbage Pickup")

    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    duty_time = models.CharField(max_length=100, blank=True, help_text="e.g., Morning (8AM - 4PM)")
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_profile')
    assigned_zone = models.ForeignKey('Zone', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_assignments')

    def __str__(self):

        return self.name



class Payment(models.Model):

    complaint=models.ForeignKey('Complaint',on_delete=models.CASCADE)

    amount=models.DecimalField(max_digits=10,decimal_places=2)

    status=models.CharField(max_length=50,default="Pending")

    date=models.DateTimeField(auto_now_add=True)

class ComplaintPricingConfig(models.Model):
    """Configuration for complaint fee pricing based on distance and urgency."""
    distance_range = models.CharField(max_length=100, help_text="e.g., '0 - 5 km', '5 - 10 km'")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    urgent_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price when priority is Urgent", default=100.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.distance_range} (Base: {self.base_price}, Urgent: {self.urgent_price})"



class Announcement(models.Model):
    ALERT_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='info')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AnnouncementRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'announcement')

    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"



class RouteAlert(models.Model):

    area=models.CharField(max_length=100)

    reason=models.TextField()

    date=models.DateField()

    resolved=models.BooleanField(default=False)

from django.core.validators import MinValueValidator, MaxValueValidator

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback - {self.rating} Stars by {self.user.username if self.user else 'Anonymous'}"

class CleaningSchedule(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]
    SERVICE_CHOICES = [
        ('Street Cleaning', 'Street Cleaning'),
        ('Garbage Pickup', 'Garbage Pickup'),
        ('Drain Cleaning', 'Drain Cleaning')
    ]
    TIME_CHOICES = [
        ('Morning', 'Morning'),
        ('Evening', 'Evening')
    ]

    area = models.CharField(max_length=150)
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_CHOICES)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    def __str__(self):
        return f"{self.service_type} at {self.area} on {self.date}"

class Zone(models.Model):
    STATUS_CHOICES = [
        ('Clean', 'Clean'),
        ('Moderate', 'Moderate'),
        ('Critical', 'Critical')
    ]
    name = models.CharField(max_length=100)
    boundary = models.JSONField(help_text="GeoJSON Polygon data")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Clean')
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_zones')
    complaint_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('garbage_truck', 'Garbage Truck'),
        ('water_tanker', 'Water Tanker'),
        ('service_vehicle', 'Service Vehicle'),
        ('sweeper', 'Road Sweeper'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active / On Duty'),
        ('Idle', 'Idle / Waiting'),
        ('In Transit', 'In Transit'),
        ('Arrived', 'Arrived'),
        ('Work in Progress', 'Work in Progress'),
        ('Completed', 'Completed'),
        ('Offline', 'Offline'),
        ('Out of Service', 'Out of Service'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled'),
    ]
    vehicle_id = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=30, choices=VEHICLE_TYPES, default='garbage_truck')
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20, blank=True)
    assigned_zone = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Moving')
    is_active = models.BooleanField(default=True)
    plate_number = models.CharField(max_length=20, blank=True)
    base_lat = models.FloatField(default=32.5736)
    base_lng = models.FloatField(default=74.0790)
    sim_phase = models.FloatField(default=0.0, help_text="Simulation phase offset for GPS trajectory")
    source_name = models.CharField(max_length=100, default='Main Depot', help_text="Starting point name, e.g., 'West Garage'")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle_id} — {self.driver_name}"

    assigned_driver = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_vehicle')
    current_complaint = models.OneToOneField('Complaint', on_delete=models.SET_NULL, null=True, blank=True, related_name='tracked_vehicle')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


class VehicleLocation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.vehicle.vehicle_id} @ {self.timestamp}"


# --- SERVICE SCHEDULING SYSTEM ---

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    urgent_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    advance_booking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    urgency_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.50)
    icon = models.CharField(max_length=50, default='bi-gear', help_text="Bootstrap icon class")

    def __str__(self):
        return self.name

class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]
    URGENCY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_bookings')
    service = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='Normal')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    address = models.TextField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    is_advance = models.BooleanField(default=False)
    advance_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    assigned_staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} - {self.user.username} ({self.scheduled_date})"

class ServicePaymentSetting(models.Model):
    gateway_name = models.CharField(max_length=100, default="Stripe")
    merchant_id = models.CharField(max_length=100, blank=True)
    merchant_key = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.gateway_name

# --- MUNICIPAL SERVICE SCHEDULING SYSTEM (UPGRADED) ---

class MunicipalServiceSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Bi-weekly', 'Bi-weekly'),
    ]
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
    ]
    
    service = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='municipal_schedules')
    area_name = models.CharField(max_length=150, help_text="e.g., Fawara Chowk")
    union_council = models.CharField(max_length=150, help_text="e.g., Model Town")
    start_time = models.TimeField()
    end_time = models.TimeField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='Daily')
    day_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK, blank=True, null=True)
    admin_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} - {self.area_name}"

class ScheduleAlert(models.Model):
    area = models.CharField(max_length=150)
    service = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="e.g., Pipe Burst Alert")
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ALERT: {self.title} ({self.area})"

class HolidayConfig(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100, help_text="e.g., Eid-ul-Fitr")
    is_active = models.BooleanField(default=True)
    special_plan = models.TextField(blank=True, help_text="Optional: Post a special waste management plan")
    
    # New Fields for Pricing Adjustments
    price_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00, help_text="e.g., 0.8 for 20% off, 1.2 for 20% surcharge")
    adjustment_description = models.CharField(max_length=200, blank=True, help_text="e.g., Festive Season Discount")
    is_pricing_active = models.BooleanField(default=False, help_text="Enable price adjustments for this day")

    # Features for Enhanced Holiday Card
    SERVICE_STATUS_CHOICES = [
        ('Available Now', '✅ Available Now'),
        ('Limited Staff', '⚠️ Limited Staff'),
        ('Fully Booked', '❌ Fully Booked'),
    ]
    HOLIDAY_TYPE_CHOICES = [
        ('Eid', 'Eid (Moon Icon)'),
        ('Public', 'Public Holiday (Flag)'),
        ('Festive', 'Festive (Gift)'),
        ('Emergency', 'Emergency (Alert)'),
    ]

    service_status = models.CharField(max_length=30, choices=SERVICE_STATUS_CHOICES, default='Available Now')
    special_services = models.TextField(blank=True, help_text="Comma-separated: Emergency handling, Road cleaning, etc.")
    coverage_tags = models.TextField(blank=True, help_text="e.g., Active During Holidays Only, Limited-Time Service")
    zones_covered = models.TextField(blank=True, help_text="Comma-separated: Zone A, Zone B, etc.")
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPE_CHOICES, default='Public')

    def __str__(self):
        return f"{self.name} on {self.date}"


# --- WALLET SYSTEM ---

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_linked = models.BooleanField(default=False)
    stripe_account_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet - Rs. {self.balance}"

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('Deposit', 'Deposit'),
        ('Payment', 'Payment'),
        ('Refund', 'Refund')
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of Rs. {self.amount} ({self.wallet.user.username})"


class ContactMessage(models.Model):
    CATEGORY_CHOICES = [
        ('General Inquiry', 'General Inquiry'),
        ('Billing Issue', 'Billing Issue'),
        ('Service Complaint', 'Service Complaint'),
        ('Feedback', 'Feedback'),
        ('Technical Support', 'Technical Support'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='General Inquiry')
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    # Admin Side
    reply = models.TextField(blank=True, null=True)
    is_replied = models.BooleanField(default=False)
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='replied_messages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Message from {self.name} ({self.category})"