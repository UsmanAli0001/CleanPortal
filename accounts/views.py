from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Complaint
import random, string

# --- USER AUTH ---
def register_view(request):
    if request.method == "POST":
        first = request.POST['first_name']
        last = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            messages.error(request,"Passwords do not match")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request,"Email already exists")
            return redirect('register')

        if len(password) < 6:
            messages.error(request,"Password must be at least 6 characters")
            return redirect('register')

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first, last_name=last
        )

        Profile.objects.create(user=user)

        try:
            send_mail(
                'Clean Portal Account',
                'Your account was created successfully',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True
            )
        except Exception as e:
            print(e)

        messages.success(request,"Account created successfully")
        return redirect('login')

    return render(request,'accounts/register.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request,"Invalid Email or Password")
            return redirect('login')

    return render(request,'accounts/login.html')


@login_required(login_url='login')
def dashboard_view(request):
    # Pass dynamic stats to dashboard if needed
    total_complaints = Complaint.objects.count()
    resolved_issues = Complaint.objects.filter(status='Resolved').count()
    pending_reports = Complaint.objects.filter(status='Waiting').count()
    area_summary = Complaint.objects.values('area').distinct().count()

    context = {
        'total_complaints': total_complaints,
        'resolved_issues': resolved_issues,
        'pending_reports': pending_reports,
        'area_summary': area_summary
    }
    return render(request, 'accounts/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.success(request,"Logged out successfully")
    return redirect('login')


# --- COMPLAINTS ---
def generate_unique_complaint_id(length=6):
    chars = string.ascii_uppercase + string.digits
    while True:
        random_id = f"CPL-{''.join(random.choices(chars, k=length))}"
        if not Complaint.objects.filter(complaint_id=random_id).exists():
            return random_id

def register_complaint(request):

    if request.method == "POST":

        complaint_id = generate_unique_complaint_id()

        image = request.FILES.get('image')
        video = request.FILES.get('video')

        complaint = Complaint.objects.create(

            complaint_id = complaint_id,

            name = request.POST.get('name'),

            email = request.POST.get('email'),

            complaint_type = request.POST.get('type'),

            area = request.POST.get('area'),

            description = request.POST.get('description'),

            image = image,

            video = video,

            status = 'Waiting'

        )

        return render(request,'accounts/complaint_success.html',{

            'complaint_id': complaint.complaint_id

        })

    return render(request,'accounts/complaint.html')


def track_complaint(request):
    complaint = None
    error = None
    if request.method == "POST":
        cid = request.POST.get('complaint_id', '').strip()
        try:
            complaint = Complaint.objects.get(complaint_id__iexact=cid)
        except Complaint.DoesNotExist:
            error = "Complaint not found. Please check your Complaint ID."
    return render(request, 'accounts/track.html', {
        'complaint': complaint,
        'error': error
    })


# --- STATIC PAGES ---
def home(request):
    # Example dynamic context
    total_complaints = Complaint.objects.count()
    resolved_issues = Complaint.objects.filter(status='Resolved').count()
    pending_reports = Complaint.objects.filter(status='Waiting').count()
    area_summary = Complaint.objects.values('area').distinct().count()

    context = {
        'total_complaints': total_complaints,
        'resolved_issues': resolved_issues,
        'pending_reports': pending_reports,
        'area_summary': area_summary
    }

    return render(request, 'accounts/home.html', context)


def about_view(request):
    return render(request, 'accounts/about.html')

def services_view(request):
    return render(request, 'accounts/services.html')

def reports_view(request):
    return render(request, 'accounts/reports.html')

def contact_view(request):
    return render(request, 'accounts/contact.html')

def pay_fee(request):
    return render(request, 'accounts/pay_fee.html')

def view_reports(request):
    return render(request, 'accounts/view_reports.html')

def schedule_view(request):
    return render(request, 'accounts/schedule_view.html') 
def maintenance_view(request):
    return render(request, 'accounts/maintenance_view.html')
def emergency_view(request):
    return render(request, 'accounts/emergency_view.html')
from django.http import HttpResponse
import csv  # or PDF library if you want PDFs

def download_reports_view(request):
    # Example: generate a simple CSV for download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Area', 'Category', 'Status'])
    # Replace this with your real report data
    writer.writerow(['2026-04-04', 'Gujrat', 'Garbage', 'Resolved'])
    writer.writerow(['2026-04-03', 'Lahore', 'Water', 'Pending'])

    return response
from django.shortcuts import render, redirect
from django.contrib import messages

def contact_view(request):
    return render(request, 'accounts/contact.html')

def submit_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Here you can save to database or send an email
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')
    return redirect('contact')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Complaint

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect('dashboard')

    complaints = Complaint.objects.all()[:5]

    total = Complaint.objects.count()

    pending = Complaint.objects.filter(status="Pending").count()

    progress = Complaint.objects.filter(status="In Progress").count()

    completed = Complaint.objects.filter(status="Completed").count()

    context = {
        'complaints': complaints,
        'total': total,
        'pending': pending,
        'progress': progress,
        'completed': completed
    }

    return render(request,'accounts/admin/admin_dashboard.html',context)
from .models import Complaint,Staff,Payment,Announcement,RouteAlert

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:

        return redirect('dashboard')

    context={

    'total':Complaint.objects.count(),

    'pending':Complaint.objects.filter(status="Pending").count(),

    'progress':Complaint.objects.filter(status="In Progress").count(),

    'completed':Complaint.objects.filter(status="Completed").count(),

    'staff':Staff.objects.count(),

    'payments':Payment.objects.count()

    }

    return render(request,'accounts/admin/admin_dashboard.html',context)
@login_required
def staff_management(request):

    staff=Staff.objects.all()

    if request.method=="POST":

        Staff.objects.create(

        name=request.POST['name'],

        phone=request.POST['phone'],

        role=request.POST['role'],

        area=request.POST['area']

        )

        return redirect('staff')

    return render(request,'accounts/admin/staff.html',{'staff':staff})
@login_required
def complaints(request):

    data=Complaint.objects.all()

    staff=Staff.objects.all()

    return render(request,'accounts/admin/complaints.html',{

    'complaints':data,

    'staff':staff

    })
@login_required
def assign(request,id):

    complaint=Complaint.objects.get(id=id)

    if request.method=="POST":

        staff_id=request.POST['staff']

        complaint.assigned_to=Staff.objects.get(id=staff_id)

        complaint.status="In Progress"

        complaint.save()

    return redirect('complaints')