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



class Complaint(models.Model):

    STATUS_CHOICES = [

        ('Waiting','Waiting'),

        ('In Progress','In Progress'),

        ('Resolved','Resolved')

    ]

    complaint_id = models.CharField(
        max_length=10,
        unique=True
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

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='Waiting'

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    def __str__(self):

        return self.complaint_id



class Notification(models.Model):

    message = models.CharField(

        max_length=255

    )

    timestamp = models.DateTimeField(

        auto_now_add=True

    )

    def __str__(self):

        return self.message
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

    def __str__(self):

        return self.name



class Payment(models.Model):

    complaint=models.ForeignKey('Complaint',on_delete=models.CASCADE)

    amount=models.DecimalField(max_digits=10,decimal_places=2)

    status=models.CharField(max_length=50,default="Pending")

    date=models.DateTimeField(auto_now_add=True)



class Announcement(models.Model):

    title=models.CharField(max_length=200)

    message=models.TextField()

    created=models.DateTimeField(auto_now=True)



class RouteAlert(models.Model):

    area=models.CharField(max_length=100)

    reason=models.TextField()

    date=models.DateField()

    resolved=models.BooleanField(default=False)
def save(self,*args,**kwargs):

    if not self.complaint_id:

        last = Complaint.objects.count()

        self.complaint_id = "CMP"+str(last+1).zfill(4)

    super().save(*args,**kwargs)