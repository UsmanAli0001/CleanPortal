from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Profile, Complaint, CleaningSchedule, ComplaintTimeline, Notification,
    Feedback, Announcement, AnnouncementRead, Staff, Payment, RouteAlert, Zone,
    DriverDetail, OperatorDetail, SupervisorDetail, WorkerDetail,
    Vehicle, VehicleLocation, ServiceCategory, ServiceBooking, ServicePaymentSetting,

    MunicipalServiceSchedule, ScheduleAlert, HolidayConfig, ComplaintPricingConfig,
    Wallet, WalletTransaction, ContactMessage,
    GalleryCategory, GalleryItem, GalleryLike, AdminNotification
)
from .forms import LoginForm, RegistrationForm
import random, string, json, math, time
from django.http import JsonResponse, HttpResponse
import csv
from django.utils import timezone
from datetime import datetime, timedelta, time as dt_time
from django.db.models import Q, Avg, Sum, Count, F
from allauth.account.models import EmailAddress
import stripe
import calendar

stripe.api_key = settings.STRIPE_SECRET_KEY

# --- GUJRAT SPECIFIC AREAS ---
GUJRAT_AREAS = [
    "Model Town", "Jalalpur Jattan Road", "Shahdowla Road", "Bhimber Road", 
    "Dinga Road", "Shadiwal Road", "G.T. Road Gujrat", "Kunjah Road", 
    "Circular Road", "Railway Road", "Fawara Chowk", "Service Mor", 
    "Shadman Colony", "Rehmania Colony", "Civil Lines",
    "Sargodha Road", "Adowal", "Muslim Pura Road", "Qadir Colony", 
    "Awan Colony", "Khokhar Colony", "Darul Islam Colony", "Star Colony", 
    "New Shadman Colony", "Gulshan Colony", "Ali Pura Road", "Jinnah Link Road", 
    "Nathuwal", "Bora", "Piara", "Fatehpur Road", "Rashid Colony", 
    "Muslimabad", "Nawaz Sharif Park", "Shah Jahangir Road"
]

# --- USER AUTH ---
def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # Use email as username
            user.is_active = True # Active immediately as requested
            user.set_password(form.cleaned_data['password'])
            user.save()

            # --- CUSTOM WELCOME EMAIL ---
            try:
                subject = "Welcome to Clean Pak Portal"
                
                # Plain text version for fallback
                text_content = f"""Dear {user.first_name},

Welcome to Clean Pak Portal!

Your account has been successfully created, and we’re excited to have you join our digital community dedicated to creating a cleaner and smarter environment.

You can now submit complaints, track progress in real-time, and stay connected with every update through our smart portal system.

━━━━━━━━━━━━━━━━━━━
✨ Your Journey in 4 Steps
From complaint to resolution — fully digital, fully traceable.
━━━━━━━━━━━━━━━━━━━

1️⃣ Register & Login: Create your free account or sign in with Google in seconds.
2️⃣ Submit Report: Describe the issue, attach photos, pin the location. Done.
3️⃣ Get Tracking ID: Receive your unique GRT ID instantly. Share & track anytime.
4️⃣ Issue Resolved: Fleet dispatched, work done, admin confirms with after-image.

━━━━━━━━━━━━━━━━━━

Together, we can build a cleaner, safer, and smarter community.

Best Regards,
Clean Pak Portal Team

Supervisor Names:
• Usman Ali
• Nida Shabir"""

                # Aesthetic HTML version
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
                        .journey-box {{ background-color: #f8fafc; border-radius: 20px; padding: 25px; margin: 30px 0; border: 1px solid #e2e8f0; }}
                        .journey-header {{ font-size: 16px; font-weight: 800; color: #3b82f6; margin-bottom: 15px; display: block; text-transform: uppercase; }}
                        .step {{ margin-bottom: 12px; font-size: 15px; }}
                        .step b {{ color: #1e40af; }}
                        .footer {{ background-color: #f1f5f9; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0; }}
                        .supervisor-box {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #eff6ff; }}
                        .supervisor-name {{ color: #2563eb; font-weight: 800; font-size: 16px; }}
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
                            <div class="welcome-title">Assalam o Alaikum, {user.first_name}! 🎉</div>
                            <p>Your account has been successfully created at <span class="brand-bold">Clean Pak Portal</span>.</p>
                            <p>We’re excited to have you join our digital community dedicated to creating a cleaner and smarter environment.</p>
                            <p>You can now submit complaints, track progress in real-time, and stay connected with every update through our smart portal system.</p>
                            
                            <div class="journey-box">
                                <span class="journey-header">✨ Your Journey in 4 Steps</span>
                                <div class="step">1️⃣ <b>Register & Login:</b> Create your free account or sign in with Google in seconds.</div>
                                <div class="step">2️⃣ <b>Submit Report:</b> Describe the issue, attach photos, pin the location. Done.</div>
                                <div class="step">3️⃣ <b>Get Tracking ID:</b> Receive your unique GRT ID instantly. Share & track anytime.</div>
                                <div class="step">4️⃣ <b>Issue Resolved:</b> Fleet dispatched, work done, admin confirms with after-image.</div>
                            </div>

                            <p>Together, we can build a cleaner, safer, and smarter community.</p>
                            
                            <div class="supervisor-box">
                                <p><b>Best Regards,</b><br><span class="brand-bold">Clean Pak Portal Team</span></p>
                                <p><b>Supervisor Names:</b></p>
                                <p>• <span class="supervisor-name">Usman Ali</span></p>
                                <p>• <span class="supervisor-name">Nida Shabir</span></p>
                            </div>
                            
                            <div style="text-align: center;">
                                <a href="{request.build_absolute_uri('/')}" class="btn">Access Portal Now</a>
                            </div>
                        </div>
                        <div class="footer">
                            <p>&copy; 2026 <b>Clean Pak Portal</b>. All rights reserved.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

                print(f"DEBUG: Attempting to send welcome email to: {user.email}")
                send_mail(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                    html_message=html_content
                )
                print(f"SUCCESS: Welcome email sent to {user.email}")
                messages.success(request, f"Registration successful! Welcome to the portal.")
                request.session['show_welcome_modal'] = True
            except Exception as e:
                print(f"ERROR: Failed to send welcome email to {user.email}: {str(e)}")
                messages.warning(request, f"Registration successful! However, there was an issue sending the welcome email: {str(e)}")

            return redirect('login')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return render(request, 'accounts/register.html', {'form': form})

    form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    # if request.user.is_authenticated:
    #     return redirect('dashboard')

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email_or_username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']

            # Lookup user by either username or email (case-insensitive)
            user_obj = User.objects.filter(
                Q(username__iexact=email_or_username) | 
                Q(email__iexact=email_or_username)
            ).first()

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = authenticate(request, username=email_or_username, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Account not verified. Please check your email.")
                    return redirect('login')
                
                login(request, user)
                
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # browser close
                
                # Redirect to dashboard
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Please check your credentials.")
            return render(request, 'accounts/login.html', {'form': form})

    form = LoginForm()
    show_welcome_modal = request.session.pop('show_welcome_modal', False)
    return render(request, 'accounts/login.html', {'form': form, 'show_welcome_modal': show_welcome_modal})

def check_email_exists(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)


@login_required(login_url='login')
def dashboard_view(request):
    # Pass dynamic stats to dashboard if needed
    user_complaints = Complaint.objects.filter(
        Q(user=request.user) | 
        (Q(user__isnull=True) & (Q(email__iexact=request.user.email) | Q(email__iexact=request.user.username))),
        payment_status=True
    )
    total_complaints = user_complaints.count()
    resolved_issues = user_complaints.filter(status='Completed').count()
    in_progress = user_complaints.filter(status='In Progress').count()
    pending_reports = user_complaints.filter(status='Pending').count()

    # Global stats for City Analytics card
    global_total = Complaint.objects.filter(payment_status=True).count()
    global_resolved = Complaint.objects.filter(status='Completed', payment_status=True).count()


    # Fetch active special pricing adjustment
    today = timezone.now().date()
    active_holiday = HolidayConfig.objects.filter(date=today, is_pricing_active=True).first()
    
    holiday_info = None
    if active_holiday:
        is_discount = active_holiday.price_multiplier < 1
        pct = abs(int((1 - active_holiday.price_multiplier) * 100)) if is_discount else abs(int((active_holiday.price_multiplier - 1) * 100))
        holiday_info = {
            'obj': active_holiday,
            'is_discount': is_discount,
            'percentage': pct
        }

    gallery_complaints = Complaint.objects.filter(
        Q(user=request.user) | (Q(user__isnull=True) & (Q(email__iexact=request.user.email) | Q(email__iexact=request.user.username))),
        status='Completed', 
        image__isnull=False, 
        after_image__isnull=False,
        payment_status=True
    ).exclude(image='').exclude(after_image='').order_by('-created_at')[:6]


    # Wallet logic
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    # Feedback stats
    reviews_qs = Feedback.objects.filter(user=request.user)
    # Primary sort: Stars (5 to 1), Secondary sort: Date
    reviews = reviews_qs.order_by('-rating', '-created_at')
    avg_rating = reviews_qs.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = reviews_qs.count()

    # Calculate rating distribution
    rating_distribution = []
    for i in range(5, 0, -1):
        count = reviews_qs.filter(rating=i).count()
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_distribution.append({
            'stars': i,
            'count': count,
            'percentage': percentage
        })


    # Fetch next upcoming city-wide holiday
    upcoming_holiday = HolidayConfig.objects.filter(
        date__gte=today,
        is_active=True
    ).order_by('date').first()

    countdown = None
    holiday_stats = {}
    if upcoming_holiday:
        countdown = (upcoming_holiday.date - today).days
        # Advanced Mini Stats for the Card
        holiday_stats = {
            'resolved_today': ComplaintTimeline.objects.filter(status='Completed', created_at__date=today).count(),
            'active_teams': Staff.objects.count(),
            'pending_requests': Complaint.objects.filter(status='Pending', payment_status=True).count(),
            'is_paid': upcoming_holiday.is_pricing_active and upcoming_holiday.price_multiplier != 1.0,
            'fee_info': f"Rs. {int(500 * upcoming_holiday.price_multiplier)}" if (upcoming_holiday.is_pricing_active and upcoming_holiday.price_multiplier != 1.0) else "Free",
        }

    context = {
        'total_complaints': total_complaints,
        'resolved_issues': resolved_issues,
        'in_progress': in_progress,
        'pending_reports': pending_reports,
        'active_holiday': holiday_info,
        'upcoming_holiday': upcoming_holiday,
        'countdown': countdown,
        'holiday_stats': holiday_stats,
        'gallery_complaints': gallery_complaints,
        'wallet_balance': wallet.balance,
        'is_wallet_linked': wallet.is_linked,
        'reviews': reviews[:20],
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'rating_dist': rating_distribution,
        'global_total': global_total,
        'global_resolved': global_resolved,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def impact_gallery_view(request):
    gallery_complaints = Complaint.objects.filter(
        Q(user=request.user) | (Q(user__isnull=True) & (Q(email__iexact=request.user.email) | Q(email__iexact=request.user.username))),
        status='Completed', 
        image__isnull=False, 
        after_image__isnull=False,
        payment_status=True
    ).exclude(image='').exclude(after_image='').order_by('-created_at')
    
@login_required(login_url='login')
def complaint_history_view(request):
    complaints = Complaint.objects.filter(
        (Q(user=request.user) | 
        (Q(user__isnull=True) & (Q(email__iexact=request.user.email) | Q(email__iexact=request.user.username)))),
        payment_status=True
    ).order_by('-created_at')

    
    # Calculate some quick stats for the user
    total = complaints.count()
    completed = complaints.filter(status='Completed').count()
    pending = complaints.filter(status__in=['Pending', 'Waiting', 'In Progress', 'Verified']).count()
    
    context = {
        'complaints': complaints,
        'total': total,
        'completed': completed,
        'pending': pending
    }
    return render(request, 'accounts/complaint_history.html', context)

@login_required(login_url='login')
def admin_complaint_history_view(request):
    if not request.user.is_staff:
        messages.error(request, "Access Denied: Administrative permissions required.")
        return redirect('dashboard')
        
    complaints = Complaint.objects.filter(payment_status=True).order_by('-created_at')
    
    context = {
        'complaints': complaints,
        'total': complaints.count(),
        'completed': complaints.filter(status='Completed').count(),
        'pending': complaints.filter(status__in=['Pending', 'Waiting', 'In Progress', 'Verified']).count(),
        'is_admin_view': True
    }
    return render(request, 'accounts/admin/complaint_history_admin.html', context)

def logout_view(request):
    is_admin = False
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        is_admin = True
    
    referer = request.META.get('HTTP_REFERER', '')
    if 'admin' in referer:
        is_admin = True

    logout(request)
    
    if is_admin:
        messages.success(request, "Admin Logout successfully")
        return redirect('admin:login')
    else:
        messages.success(request, "Logged out")
        return redirect('login')



# --- UTILITIES ---
def calculate_complaint_fee(complaint):
    """Calculates the final fee for a complaint based on tier, priority, and special day adjustments."""
    if not complaint.fee_tier:
        # Fallback to default pricing if no tier specified (e.g. 0-5km)
        tier = ComplaintPricingConfig.objects.filter(is_active=True).first()
        if not tier:
            return Decimal("0.00"), Decimal("1.0"), "No pricing configured"
    else:
        tier = complaint.fee_tier

    # Determine base price based on priority
    base_price = tier.urgent_price if complaint.priority == 'Urgent' else tier.base_price
    
    # Dynamic Grievance Fee from ServiceCategory
    grievance_fee = Decimal("0.00")
    try:
        service = ServiceCategory.objects.get(name=complaint.complaint_type)
        grievance_fee = service.base_price
    except ServiceCategory.DoesNotExist:
        # Fallback to Rs. 500 if not found
        grievance_fee = Decimal("500.00")
    
    # Check for active holiday pricing
    today = timezone.now().date()
    holiday = HolidayConfig.objects.filter(date=today, is_pricing_active=True).first()
    
    multiplier = Decimal("1.0")
    description = "Standard Pricing"
    
    if holiday:
        multiplier = holiday.price_multiplier
        description = holiday.adjustment_description or f"{holiday.name} Adjustment"

    final_amount = (base_price + grievance_fee) * multiplier
    return round(final_amount, 2), multiplier, description

# --- COMPLAINTS ---
def register_complaint(request):

    if request.method == "POST":
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        tier_id = request.POST.get('fee_tier')
        priority = request.POST.get('priority', 'Normal')

        complaint = Complaint.objects.create(
            user = request.user if request.user.is_authenticated else None,
            name = request.POST.get('name'),
            email = request.POST.get('email'),
            complaint_type = request.POST.get('type'),
            area = request.POST.get('area'),
            description = request.POST.get('description'),
            priority = priority,
            image = image,
            video = video,
            latitude = request.POST.get('latitude'),
            longitude = request.POST.get('longitude'),
            status = 'Pending',
            payment_status = False,
            fee_tier_id = tier_id
        )

        
        # Calculate initial fee to show on checkout
        amount, mult, desc = calculate_complaint_fee(complaint)
        complaint.final_amount = amount
        complaint.save()
        
        # Save ID to session and redirect to stripe checkout
        request.session['pending_complaint_id'] = complaint.id
        return redirect('stripe_checkout')

    # For GET request, provide active pricing tiers and service categories
    pricings_qs = ComplaintPricingConfig.objects.filter(is_active=True)
    
    import re
    def get_distance_key(p):
        numbers = re.findall(r'\d+', p.distance_range)
        return int(numbers[0]) if numbers else 9999
        
    pricings = list(pricings_qs)
    pricings.sort(key=get_distance_key)
    
    categories = ServiceCategory.objects.all()
    return render(request,'accounts/complaint.html', {'pricings': pricings, 'categories': categories})

def stripe_checkout(request):
    complaint_id = request.session.get('pending_complaint_id')
    if not complaint_id:
        return redirect('register_complaint')
    
    complaint = Complaint.objects.get(id=complaint_id)
    amount, mult, desc = calculate_complaint_fee(complaint)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pkr',
                    'unit_amount': int(amount * 100),
                    'product_data': {
                        'name': f'Complaint Registration Fee ({complaint.complaint_type})',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('stripe_success')),
            cancel_url=request.build_absolute_uri(reverse('stripe_cancel')),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('register_complaint')

def stripe_success(request):
    complaint_id = request.session.get('pending_complaint_id')
    if not complaint_id:
        return redirect('register_complaint')
    
    complaint = Complaint.objects.get(id=complaint_id)
    complaint.payment_status = True
    complaint.save()

    # Create actual payment record
    Payment.objects.create(
        complaint=complaint,
        amount=complaint.final_amount,
        status="Paid"
    )

    # Deduct from Wallet Balance for the complaint fee
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    WalletTransaction.objects.create(
        wallet=wallet,
        amount=complaint.final_amount,
        transaction_type='Payment',
        description=f"Direct Payment for Complaint {complaint.complaint_id} via Stripe"
    )
    wallet.balance -= complaint.final_amount
    wallet.save()


    
    del request.session['pending_complaint_id']
    return render(request, 'accounts/complaint_success.html', {'complaint_id': complaint.complaint_id})

# --- WALLET VIEWS ---

@login_required(login_url='login')
def wallet_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-timestamp')
    
    context = {
        'wallet': wallet,
        'transactions': transactions
    }
    return render(request, 'accounts/wallet.html', context)

@login_required(login_url='login')
def link_stripe_account(request):
    if request.method == "POST":
        stripe_account_id = request.POST.get('stripe_account_id')
        stripe_email = request.POST.get('stripe_email')
        
        if not stripe_account_id or not stripe_email:
            messages.error(request, "Please fill in all details.")
            return redirect('wallet')
            
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.stripe_account_id = stripe_account_id
        wallet.stripe_email = stripe_email
        wallet.is_linked = True
        wallet.save()
        
        messages.success(request, "Stripe account linked!")
        return redirect('wallet')
    
    return redirect('wallet')

@login_required(login_url='login')
def wallet_deposit(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        if not amount or float(amount) <= 0:
            messages.error(request, "Please enter a valid amount.")
            return redirect('wallet')
        
        # Store amount in session for the success callback
        request.session['pending_deposit_amount'] = str(amount)
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'pkr',
                        'unit_amount': int(float(amount) * 100),
                        'product_data': {
                            'name': 'Wallet Deposit',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('wallet_deposit_success')),
                cancel_url=request.build_absolute_uri(reverse('wallet')),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('wallet')
    
    return redirect('wallet')

@login_required(login_url='login')
def wallet_deposit_success(request):
    amount_str = request.session.get('pending_deposit_amount')
    if not amount_str:
        return redirect('wallet')
    
    amount = Decimal(amount_str)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    # Update balance
    wallet.balance += amount
    wallet.save()
    
    # Create transaction record
    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type='Deposit',
        description="Founds added via Stripe"
    )
    
    del request.session['pending_deposit_amount']
    messages.success(request, f"Successfully deposited Rs. {amount} into your wallet.")
    return redirect('wallet')

def stripe_cancel(request):
    complaint_id = request.session.get('pending_complaint_id')
    if complaint_id:
        Complaint.objects.filter(id=complaint_id).delete()
        del request.session['pending_complaint_id']
    messages.error(request, "Payment was cancelled. Complaint not submitted.")
    return redirect('register_complaint')



def track_complaint(request):
    complaint = None
    error = None
    timeline = None
    if request.method == "POST":
        cid = request.POST.get('complaint_id', '').strip()
        try:
            complaint = Complaint.objects.get(complaint_id__iexact=cid)
            raw_timeline = complaint.timeline.all().order_by('-created_at')
            
            dedup_timeline = []
            seen = {}
            for t in raw_timeline:
                # Define statuses that should ALWAYS be shown as separate events (e.g., Fleet movements)
                is_fleet_update = t.status in ['Fleet Update', 'Fleet Assigned']
                
                if is_fleet_update or t.status not in seen:
                    entry = {
                        'status': t.status,
                        'description': t.description,
                        'created_at': t.created_at
                    }
                    dedup_timeline.append(entry)
                    if not is_fleet_update:
                        seen[t.status] = entry
                else:
                    # For standard statuses, merge descriptions if they differ to keep history compact but detailed
                    if t.description not in seen[t.status]['description']:
                        seen[t.status]['description'] = seen[t.status]['description'] + " | " + t.description
            
            timeline = dedup_timeline

            if not complaint.payment_status:
                messages.warning(request, "This complaint has been recorded but payment is still pending. Some features may be limited.")
        except Complaint.DoesNotExist:
            error = "Complaint not found. Please check your Complaint ID."
    
    assigned_vehicle = None
    if complaint:
        assigned_vehicle = Vehicle.objects.filter(current_complaint=complaint).first()
    
    is_owner = False
    if complaint and request.user.is_authenticated:
        is_owner = (complaint.user == request.user or complaint.email == request.user.email or complaint.email == request.user.username)

    return render(request, 'accounts/track.html', {
        'complaint': complaint,
        'timeline': timeline,
        'error': error,
        'is_owner': is_owner,
        'vehicle': assigned_vehicle
    })

def download_complaint_report(request, cid):
    try:
        complaint = Complaint.objects.get(complaint_id__iexact=cid)
        if not complaint.payment_status:
            return redirect('track')
    except Complaint.DoesNotExist:
        return redirect('track')
        
    return render(request, 'accounts/report_print.html', {'complaint': complaint})


# --- STATIC PAGES ---
def home(request):
    # Example dynamic context
    total_complaints = Complaint.objects.count()
    resolved_issues = Complaint.objects.filter(status='Resolved').count()
    pending_reports = Complaint.objects.filter(status='Waiting').count()
    area_summary = Complaint.objects.values('area').distinct().count()

    # Fetch top 3 latest feedbacks with high ratings (4 or 5 stars)
    feedbacks = Feedback.objects.filter(rating__gte=4).order_by('-created_at')[:3]

    context = {
        'total_complaints': total_complaints,
        'resolved_issues': resolved_issues,
        'pending_reports': pending_reports,
        'area_summary': len(GUJRAT_AREAS),
        'feedbacks': feedbacks,
    }

    return render(request, 'accounts/home.html', context)


def about_view(request):
    return render(request, 'accounts/about.html')

@login_required(login_url='login')
def photo_gallery_view(request):
    """View to display the professional Photo Gallery for users."""
    items_qs = GalleryItem.objects.filter(show_on_homepage=True).order_by('-published_at', '-created_at')
    categories = GalleryCategory.objects.all()
    
    # Filter logic
    category_id = request.GET.get('category')
    area = request.GET.get('area')
    status = request.GET.get('status')
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if category_id:
        items_qs = items_qs.filter(category_id=category_id)
    if area:
        items_qs = items_qs.filter(area__icontains=area)
    if status:
        items_qs = items_qs.filter(status=status)
    if search:
        items_qs = items_qs.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(area__icontains=search))
    
    if sort == 'liked':
        items_qs = items_qs.order_by('-likes_count')
    elif sort == 'oldest':
        items_qs = items_qs.order_by('created_at')

    # Get user likes for UI state
    user_likes = []
    if request.user.is_authenticated:
        user_likes = GalleryLike.objects.filter(user=request.user).values_list('gallery_item_id', flat=True)

    # Global Stats for Sidebar/Header
    stats = {
        'total_resolved': Complaint.objects.filter(status='Completed').count(),
        'total_projects': GalleryItem.objects.count(),
        'total_likes': GalleryItem.objects.aggregate(Sum('likes_count'))['likes_count__sum'] or 0,
        'total_views': GalleryItem.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0,
        'most_active_area': Complaint.objects.values('area').annotate(count=Count('id')).order_by('-count').first()
    }

    context = {
        'items': items_qs,
        'categories': categories,
        'user_likes': user_likes,
        'stats': stats,
        'gujrat_areas': GUJRAT_AREAS
    }
    return render(request, 'accounts/photo_gallery.html', context)

@csrf_exempt
def gallery_like_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        item = get_object_or_404(GalleryItem, id=item_id)
        
        user = request.user if request.user.is_authenticated else None
        ip = request.META.get('REMOTE_ADDR')
        
        # Check if already liked
        like_filter = Q(gallery_item=item)
        if user:
            like_filter &= Q(user=user)
        else:
            like_filter &= Q(ip_address=ip) & Q(user__isnull=True)
            
        existing_like = GalleryLike.objects.filter(like_filter).first()
        
        if existing_like:
            existing_like.delete()
            item.likes_count = max(0, item.likes_count - 1)
            item.save()
            return JsonResponse({'status': 'unliked', 'likes_count': item.likes_count})
        else:
            GalleryLike.objects.create(gallery_item=item, user=user, ip_address=ip)
            item.likes_count += 1
            item.save()
            return JsonResponse({'status': 'liked', 'likes_count': item.likes_count})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def gallery_view_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        # Use update() to avoid triggering post_save signals for view counts
        GalleryItem.objects.filter(id=item_id).update(views_count=F('views_count') + 1)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def admin_gallery_view(request):
    """Dashboard view for Gallery Administration."""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    total_posts = GalleryItem.objects.count()
    total_likes = GalleryItem.objects.aggregate(Sum('likes_count'))['likes_count__sum'] or 0
    total_views = GalleryItem.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    featured_posts = GalleryItem.objects.filter(is_featured=True).count()
    hidden_posts = GalleryItem.objects.filter(show_on_homepage=False).count()
    
    today = timezone.now().date()
    
    def get_gallery_trend(days_count=None, months_count=None, is_all=False):
        if is_all:
            first_item = GalleryItem.objects.order_by('created_at').first()
            if first_item:
                # Use local time for consistent date logic
                start_date = timezone.localtime(first_item.created_at).date()
                num_months = (today.year - start_date.year) * 12 + (today.month - start_date.month) + 1
            else:
                num_months = 1
            is_yearly = True
        elif months_count:
            num_months = months_count
            is_yearly = True
        else:
            start_date = today - timedelta(days=days_count)
            is_yearly = False
            
        labels = []
        uploads = []
        likes = []
        
        if is_yearly:
            # Dynamic month loop (handles 12 months or 'All' months)
            for i in range(num_months - 1, -1, -1):
                # Calculate year and month correctly
                year = today.year
                month = today.month - i
                while month <= 0:
                    month += 12
                    year -= 1
                
                # Label: Jan, Feb, Mar ...
                label = calendar.month_name[month][:3]
                
                # If more than 12 months (All), append year for clarity
                if num_months > 12:
                    label += f" {str(year)[2:]}"
                
                labels.append(label)
                
                uploads.append(GalleryItem.objects.filter(created_at__year=year, created_at__month=month).count())
                likes.append(GalleryLike.objects.filter(created_at__year=year, created_at__month=month).count())
        else:
            for i in range(days_count - 1, -1, -1):
                d = today - timedelta(days=i)
                labels.append(d.strftime('%b %d'))
                
                uploads.append(GalleryItem.objects.filter(created_at__date=d).count())
                likes.append(GalleryLike.objects.filter(created_at__date=d).count())
                
        return {
            'labels': labels,
            'uploads': uploads,
            'likes': likes
        }

    trend_data = {
        'weekly': get_gallery_trend(days_count=7),
        'monthly': get_gallery_trend(days_count=30),
        'yearly': get_gallery_trend(months_count=12),
        'all': get_gallery_trend(is_all=True)
    }

    most_liked = GalleryItem.objects.order_by('-likes_count')[:5]

    context = {
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_views': total_views,
        'featured_posts': featured_posts,
        'hidden_posts': hidden_posts,
        'trend_data': json.dumps(trend_data),
        'most_liked': most_liked,
        'is_admin_view': True
    }
    return render(request, 'accounts/admin/admin_gallery_dashboard.html', context)

@login_required
def admin_gallery_list(request):
    if not request.user.is_staff: return redirect('dashboard')
    
    items = GalleryItem.objects.all().order_by('-complaint__complaint_id', '-created_at')
    
    # Filters
    cat = request.GET.get('category')
    area = request.GET.get('area')
    if cat: items = items.filter(category_id=cat)
    if area: items = items.filter(area=area)
    
    categories = GalleryCategory.objects.all()
    
    return render(request, 'accounts/admin/admin_gallery_list.html', {
        'items': items,
        'categories': categories,
        'gujrat_areas': GUJRAT_AREAS
    })

@login_required
def admin_gallery_upload(request, pk=None):
    if not request.user.is_staff: return redirect('dashboard')
    
    item = get_object_or_404(GalleryItem, pk=pk) if pk else None
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        area = request.POST.get('area')
        status = request.POST.get('status')
        complaint_id_raw = request.POST.get('complaint_id')
        
        before_img = request.FILES.get('before_image')
        after_img = request.FILES.get('after_image')
        
        is_featured = request.POST.get('is_featured') == 'on'
        show_on_homepage = request.POST.get('show_on_homepage') == 'on'
        
        complaint = None
        if complaint_id_raw:
            complaint = Complaint.objects.filter(complaint_id__iexact=complaint_id_raw).first()

        if item:
            item.title = title
            item.description = description
            item.category_id = category_id
            item.area = area
            item.status = status
            item.complaint = complaint
            item.is_featured = is_featured
            item.show_on_homepage = show_on_homepage
            if before_img: item.before_image = before_img
            if after_img: item.after_image = after_img
            item.save()
            messages.success(request, "Gallery item updated.")
        else:
            GalleryItem.objects.create(
                title=title, description=description, category_id=category_id,
                area=area, status=status, complaint=complaint,
                before_image=before_img, after_image=after_img,
                is_featured=is_featured, show_on_homepage=show_on_homepage,
                published_at=timezone.now()
            )
            messages.success(request, "New gallery item published!")
            
        return redirect('admin_gallery_list')

    categories = GalleryCategory.objects.all()
    return render(request, 'accounts/admin/admin_gallery_form.html', {
        'item': item,
        'categories': categories,
        'gujrat_areas': GUJRAT_AREAS
    })

@login_required
def admin_gallery_delete(request, pk):
    if not request.user.is_staff: return redirect('dashboard')
    get_object_or_404(GalleryItem, pk=pk).delete()
    messages.warning(request, "Gallery item removed.")
    return redirect('admin_gallery_list')


@login_required
def admin_gallery_categories(request):
    if not request.user.is_staff: return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon', 'image')
        color = request.POST.get('color', '#3b82f6')
        GalleryCategory.objects.create(name=name, icon=icon, color=color)
        messages.success(request, f"Category '{name}' added.")
        return redirect('admin_gallery_categories')
        
    categories = GalleryCategory.objects.all()
    return render(request, 'accounts/admin/admin_gallery_categories.html', {'categories': categories})

@login_required
def admin_category_delete(request, pk):
    if not request.user.is_staff: return redirect('dashboard')
    get_object_or_404(GalleryCategory, pk=pk).delete()
    messages.warning(request, "Category removed.")
    return redirect('admin_gallery_categories')

@login_required
def api_gallery_toggle(request):
    if not request.user.is_staff: return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        data = json.loads(request.body)
        item = GalleryItem.objects.get(id=data.get('id'))
        field = data.get('field')
        if field == 'featured':
            item.is_featured = not item.is_featured
        elif field == 'visible':
            item.show_on_homepage = not item.show_on_homepage
        item.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def pricing_catalog_view(request):
    """View to display the full pricing and service category catalog."""
    context = {
        'service_categories': ServiceCategory.objects.all()
    }
    return render(request, 'accounts/pricing_catalog.html', context)

def services_view(request):
    """Dedicated view for the comprehensive services hub."""
    return render(request, 'accounts/services.html')

def reports_view(request):
    import json
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    import calendar

    # Overview stats (All-time)
    total_complaints = Complaint.objects.filter(payment_status=True).count()
    resolved_complaints = Complaint.objects.filter(status='Completed', payment_status=True).count()
    pending_complaints = Complaint.objects.filter(status='Pending', payment_status=True).count()
    in_progress = Complaint.objects.filter(status__in=['Verified', 'In Progress'], payment_status=True).count()
    now = timezone.now()
    today = timezone.localtime(now).date()

    def get_report_period_data(days_count=None, months_count=None, is_all=False):
        if is_all:
            period_qs = Complaint.objects.filter(payment_status=True)
            is_yearly = True
            first_complaint = period_qs.order_by('created_at').first()
            start_date = first_complaint.created_at.date() if first_complaint else today
        elif months_count:
            start_date = today - timedelta(days=months_count * 30)
            is_yearly = True
            period_qs = Complaint.objects.filter(created_at__date__gte=start_date, payment_status=True)
        else:
            start_date = today - timedelta(days=days_count)
            is_yearly = False
            period_qs = Complaint.objects.filter(created_at__date__gte=start_date, payment_status=True)

        # 1. Area breakdown
        area_counts = period_qs.values('area').annotate(count=Count('id'))
        counts_dict = {item['area']: item['count'] for item in area_counts}
        display_areas = GUJRAT_AREAS.copy()
        for area in counts_dict:
            if area not in display_areas: display_areas.append(area)
        area_complaints = [counts_dict.get(a, 0) for a in display_areas]

        # 2. Category breakdown
        type_qs = period_qs.values('complaint_type').annotate(count=Count('id')).order_by('-count')
        types = [item['complaint_type'] for item in type_qs]
        type_counts = [item['count'] for item in type_qs]

        # 3. Status Distribution
        status_summary = period_qs.values('status').annotate(count=Count('id'))
        status_labels = [item['status'] for item in status_summary]
        status_data = [item['count'] for item in status_summary]

        # 4. Trend Data
        labels = []
        counts = []
        if is_all:
            # For all time, we show by month but covering the whole range
            first_c = Complaint.objects.order_by('created_at').first()
            if first_c:
                curr = first_c.created_at.replace(day=1).date()
                while curr <= today:
                    label = calendar.month_name[curr.month] # January, February, etc.
                    labels.append(label)
                    counts.append(period_qs.filter(created_at__year=curr.year, created_at__month=curr.month).count())
                    # Move to next month
                    if curr.month == 12: curr = curr.replace(year=curr.year+1, month=1)
                    else: curr = curr.replace(month=curr.month+1)
            else:
                labels = ["No Data"]
                counts = [0]
        elif is_yearly:
            for i in range(11, -1, -1):
                first = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
                m = first.month
                y = first.year
                label = calendar.month_name[m] # January, February, etc.
                labels.append(label)
                counts.append(period_qs.filter(created_at__year=y, created_at__month=m).count())
        else:
            for i in range(days_count - 1, -1, -1):
                d = today - timedelta(days=i)
                labels.append(d.strftime('%b %d'))
                counts.append(period_qs.filter(created_at__date=d).count())

        return {
            'areas': display_areas,
            'area_complaints': area_complaints,
            'types': types,
            'type_counts': type_counts,
            'status_labels': status_labels,
            'status_data': status_data,
            'trend_labels': labels,
            'trend_counts': counts,
            'total_in_period': period_qs.count()
        }

    chart_data = {
        'all': get_report_period_data(is_all=True),
        'weekly': get_report_period_data(days_count=7),
        'monthly': get_report_period_data(days_count=30),
        'yearly': get_report_period_data(months_count=12)
    }

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'in_progress': in_progress,
        'total_zones': len(GUJRAT_AREAS),
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'accounts/reports.html', context)
    
def admin_city_reports_view(request):
    import json
    from django.db.models import Count, Q, Avg
    from django.utils import timezone
    from datetime import timedelta
    import calendar
    from accounts.models import Complaint, ComplaintTimeline, Staff, Vehicle

    if not request.user.is_staff:
        messages.error(request, "Access Denied: Administrative permissions required.")
        return redirect('dashboard')

    now = timezone.now()
    today = timezone.localtime(now).date()

    def get_period_data(days_count=None, months_count=None, is_all=False):
        if is_all:
            period_qs = Complaint.objects.filter(payment_status=True)
            is_yearly = True
            first_complaint = period_qs.order_by('created_at').first()
            if first_complaint:
                start_date = first_complaint.created_at.date()
                # Calculate total months from start to now
                num_months = (today.year - start_date.year) * 12 + (today.month - start_date.month) + 1
            else:
                start_date = today
                num_months = 1
        elif months_count:
            start_date = today - timedelta(days=months_count * 30)
            is_yearly = True
            period_qs = Complaint.objects.filter(created_at__date__gte=start_date, payment_status=True)
            num_months = months_count
        else:
            start_date = today - timedelta(days=days_count)
            is_yearly = False
            period_qs = Complaint.objects.filter(created_at__date__gte=start_date, payment_status=True)
            num_months = days_count
        
        # 1. Category Breakdown
        type_qs = period_qs.values('complaint_type').annotate(count=Count('id')).order_by('-count')
        types = [item['complaint_type'] for item in type_qs]
        type_counts = [item['count'] for item in type_qs]

        # 2. Trend Data (Submissions, Resolution, Activity)
        labels = []
        submissions = []
        resolutions = []
        activities = []
        trips = []
        
        if is_yearly:
            # Dynamic month loop
            for i in range(num_months - 1, -1, -1):
                # Calculate year and month correctly
                year = today.year
                month = today.month - i
                while month <= 0:
                    month += 12
                    year -= 1
                
                # Label: "January" or "Jan 2026" if All/Yearly
                label = calendar.month_name[month][:3]
                if num_months > 12:
                    label += f" {str(year)[2:]}"
                elif is_all or months_count == 12:
                    # Optional: include year for clarity even if exactly 12 months? 
                    # User requested Jan, Feb, March.
                    label = calendar.month_name[month] # Full month name
                
                labels.append(label)
                
                m_qs = period_qs.filter(created_at__year=year, created_at__month=month)
                submissions.append(m_qs.count())
                
                # Resolution
                comp_tl = ComplaintTimeline.objects.filter(status='Completed', created_at__year=year, created_at__month=month)
                total_days = 0
                count = 0
                for tl in comp_tl:
                    duration = tl.created_at - tl.complaint.created_at
                    total_days += duration.total_seconds() / 86400.0
                    count += 1
                resolutions.append(round(total_days / count, 1) if count > 0 else 0)
                
                # Activity
                signups = User.objects.filter(date_joined__year=year, date_joined__month=month).count()
                submitters = m_qs.values('user').distinct().count()
                activities.append(signups + submitters)
                
                # Activity (Vehicle Working)
                working = Vehicle.objects.filter(assign_date__year=year, assign_date__month=month).count()
                trips.append(working)
        else:
            # Last N Days
            for i in range(days_count - 1, -1, -1):
                d = today - timedelta(days=i)
                label = d.strftime('%b %d')
                labels.append(label)
                
                d_qs = period_qs.filter(created_at__date=d)
                submissions.append(d_qs.count())
                
                # Resolution
                comp_tl = ComplaintTimeline.objects.filter(status='Completed', created_at__date=d)
                total_days = 0
                count = 0
                for tl in comp_tl:
                    duration = tl.created_at - tl.complaint.created_at
                    total_days += duration.total_seconds() / 86400.0
                    count += 1
                resolutions.append(round(total_days / count, 1) if count > 0 else 0)
                
                # Activity
                signups = User.objects.filter(date_joined__date=d).count()
                submitters = d_qs.values('user').distinct().count()
                activities.append(signups + submitters)

                # Activity (Vehicle Working - Based on Assign Date)
                working = Vehicle.objects.filter(assign_date=d).count()
                trips.append(working)

        # 3. Area Breakdown
        area_counts = period_qs.values('area').annotate(count=Count('id'))
        counts_dict = {item['area']: item['count'] for item in area_counts}
        display_areas = GUJRAT_AREAS.copy()
        for area in counts_dict:
            if area not in display_areas: display_areas.append(area)
        area_complaints = [counts_dict.get(a, 0) for a in display_areas]

        # 4. Staff Performance
        staff_qs = Staff.objects.exclude(
            email__startswith="driver"
        ).exclude(
            email__startswith="worker"
        ).annotate(
            total_assigned=Count('complaint', filter=Q(complaint__created_at__date__gte=start_date)),
            total_completed=Count('complaint', filter=Q(complaint__status='Completed', complaint__created_at__date__gte=start_date))
        ).order_by('-total_assigned')[:5]
        staff_names = [s.name for s in staff_qs]
        staff_assigned = [s.total_assigned for s in staff_qs]
        staff_resolved = [s.total_completed for s in staff_qs]

        # 5. Issue Type vs Resolution
        type_res_qs = period_qs.values('complaint_type').annotate(
            total=Count('id'),
            resolved=Count('id', filter=Q(status='Completed'))
        ).order_by('-total')
        type_res_labels = [item['complaint_type'] for item in type_res_qs]
        type_res_resolved = [item['resolved'] for item in type_res_qs]
        type_res_unresolved = [item['total'] - item['resolved'] for item in type_res_qs]

        # 6. Vehicle Activity (Real Metrics) - Already populated in the loops above

        return {
            'labels': labels,
            'submissions': submissions,
            'resolutions': resolutions,
            'activities': activities,
            'trips': trips,
            'types': types,
            'type_counts': type_counts,
            'areas': display_areas,
            'area_complaints': area_complaints,
            'staff_names': staff_names,
            'staff_assigned': staff_assigned,
            'staff_resolved': staff_resolved,
            'type_res_labels': type_res_labels,
            'type_res_resolved': type_res_resolved,
            'type_res_unresolved': type_res_unresolved,
            'total_in_period': period_qs.count()
        }

    # Pre-calculate all sets including All time
    weekly_data = get_period_data(days_count=7)
    monthly_data = get_period_data(days_count=30)
    yearly_data = get_period_data(months_count=12)
    all_time_data = get_period_data(is_all=True)

    # Global Stats
    total_complaints = Complaint.objects.filter(payment_status=True).count()
    pending_complaints = Complaint.objects.filter(status='Pending', payment_status=True).count()
    active_vehicles = Vehicle.objects.filter(is_active=True).count()
    
    # SLA Monitoring
    sla_threshold = timezone.now() - timedelta(hours=3)
    sla_violations = Complaint.objects.filter(priority='Urgent', created_at__lt=sla_threshold, payment_status=True).exclude(status='Completed')

    context = {
        'chart_data': json.dumps({
            'weekly': weekly_data,
            'monthly': monthly_data,
            'yearly': yearly_data,
            'all': all_time_data
        }),
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'active_vehicles': active_vehicles,
        'sla_violations': sla_violations,
        'total_zones': len(GUJRAT_AREAS),
        'is_admin_view': True,
        # Fallback for initial load (All time)
        'initial_all': all_time_data
    }
    return render(request, 'accounts/admin/city_reports_admin.html', context)


@ensure_csrf_cookie
def contact_view(request):
    return render(request, 'accounts/contact.html')

def pay_fee(request):
    return render(request, 'accounts/pay_fee.html')

def view_reports(request):
    return render(request, 'accounts/view_reports.html')

def schedule_view(request):
    schedules = CleaningSchedule.objects.all().order_by('date', 'time_slot')
    schedules_data = []
    for s in schedules:
        schedules_data.append({
            'id': s.id,
            'area': s.area,
            'date': s.date.strftime('%Y-%m-%d'),
            'time_slot': s.time_slot,
            'service_type': s.service_type,
            'status': s.status,
        })
    return render(request, 'accounts/schedule_view.html', {'schedules_json': json.dumps(schedules_data)}) 

def maintenance_view(request):
    return render(request, 'accounts/maintenance_view.html')

def emergency_view(request):
    return render(request, 'accounts/emergency_view.html')

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

@csrf_protect
def submit_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        category = request.POST.get('category', 'General Inquiry')
        subject = request.POST.get('subject', 'No Subject')
        message = request.POST.get('message')
        
        # Save to database
        msg = ContactMessage.objects.create(
            name=name,
            email=email,
            category=category,
            subject=subject,
            message=message
        )
        
        # Optional: Send a console email for debug/demo
        try:
            full_msg = f"Message from {name} ({email})\nCategory: {category}\n\n{message}"
            send_mail(
                f"Contact Inquiry: {subject}",
                full_msg,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER], # Send to admin
                fail_silently=True
            )
        except:
            pass

        messages.success(request, "Your message has been sent!")
        return redirect('contact')
    return redirect('contact')

@login_required
def admin_contact_messages(request):
    if not request.user.is_staff:
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
        
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin/contact_messages.html', {'contact_messages': messages_list})

@login_required
def admin_reply_contact(request, id):
    if not request.user.is_staff:
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
        
    msg = get_object_or_404(ContactMessage, id=id)
    
    if request.method == 'POST':
        try:
            reply_content = request.POST.get('reply')
            msg.reply = reply_content
            msg.is_replied = True
            msg.replied_by = request.user
            msg.replied_at = timezone.now()
            msg.save()
            
            messages.success(request, f"Reply saved and notification sent to {msg.email}.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")


            
        return redirect('admin_contact_messages')
        
    return render(request, 'accounts/admin/reply_contact.html', {'msg': msg})

@login_required
def delete_contact_message(request, id):
    if not request.user.is_staff:
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
        
    msg = get_object_or_404(ContactMessage, id=id)
    msg.delete()
    messages.warning(request, "Contact inquiry deleted.")
    return redirect('admin_contact_messages')

@login_required
def admin_dashboard(request):
    """
    Renders the main administrative dashboard. 
    Restricted to users with 'is_staff' permission.
    """
    if not request.user.is_staff:
        messages.error(request, "Access Denied: Administrative permissions required.")
        return redirect('dashboard')

    # Safe counts for Field Staff (Specific Staff Model)
    try:
        field_staff_count = Staff.objects.count()
    except (NameError, Exception):
        field_staff_count = 0

    # Administrative staff (Users with is_staff=True)
    admin_count = User.objects.filter(is_staff=True).count()

    # Revenue Calculations
    now = timezone.now()
    weekly_start = now - timedelta(days=7)
    monthly_start = now - timedelta(days=30)
    yearly_start = now - timedelta(days=365)

    weekly_rev = Payment.objects.filter(date__gte=weekly_start, status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_rev = Payment.objects.filter(date__gte=monthly_start, status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    yearly_rev = Payment.objects.filter(date__gte=yearly_start, status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_rev = Payment.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0

    # Latest Transactions
    recent_payments = Payment.objects.all().order_by('-date')[:5]

    context = {
        'total': Complaint.objects.filter(payment_status=True).count(),
        'pending': Complaint.objects.filter(status="Pending", payment_status=True).count(),
        'progress': Complaint.objects.filter(status="In Progress", payment_status=True).count(),
        'completed': Complaint.objects.filter(status="Completed", payment_status=True).count(),
        'staff': field_staff_count,
        'admins': admin_count,
        'payments_count': Payment.objects.count(),
        'feedback_count': Feedback.objects.count(),
        'zones_count': len(GUJRAT_AREAS),
        'active_vehicles': Vehicle.objects.filter(is_active=True).count(),
        'weekly_revenue': weekly_rev,
        'monthly_revenue': monthly_rev,
        'yearly_revenue': yearly_rev,
        'total_revenue': total_rev,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'accounts/admin/admin_dashboard.html', context)

@login_required
def api_overdue_complaints(request):
    """Returns complaints that have exceeded their SLA time threshold.
    Normal complaints: 8 hours, Urgent complaints: 3 hours.
    Only considers non-completed, paid complaints."""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    now = timezone.now()
    normal_threshold = now - timedelta(hours=8)
    urgent_threshold = now - timedelta(hours=3)

    # Normal complaints older than 8 hours that are NOT completed/cancelled
    overdue_normal = Complaint.objects.filter(
        priority='Normal',
        payment_status=True,
        created_at__lte=normal_threshold
    ).exclude(status__in=['Completed', 'Cancelled']).order_by('-created_at')

    # Urgent complaints older than 3 hours that are NOT completed/cancelled
    overdue_urgent = Complaint.objects.filter(
        priority='Urgent',
        payment_status=True,
        created_at__lte=urgent_threshold
    ).exclude(status__in=['Completed', 'Cancelled']).order_by('-created_at')

    results = []
    for c in overdue_urgent:
        elapsed = now - c.created_at
        hours = int(elapsed.total_seconds() // 3600)
        mins = int((elapsed.total_seconds() % 3600) // 60)
        results.append({
            'id': c.complaint_id,
            'type': c.complaint_type,
            'area': c.area,
            'priority': 'Urgent',
            'status': c.status,
            'name': c.name,
            'created_at': c.created_at.strftime('%d %b %Y, %I:%M %p'),
            'elapsed': f'{hours}h {mins}m',
            'threshold': '3 hours',
        })

    for c in overdue_normal:
        elapsed = now - c.created_at
        hours = int(elapsed.total_seconds() // 3600)
        mins = int((elapsed.total_seconds() % 3600) // 60)
        results.append({
            'id': c.complaint_id,
            'type': c.complaint_type,
            'area': c.area,
            'priority': 'Normal',
            'status': c.status,
            'name': c.name,
            'created_at': c.created_at.strftime('%d %b %Y, %I:%M %p'),
            'elapsed': f'{hours}h {mins}m',
            'threshold': '8 hours',
        })

    return JsonResponse({
        'status': 'success',
        'overdue_count': len(results),
        'complaints': results
    })

@login_required
def admin_wallet_view(request):
    """Administrative view for system revenue totals and transaction records."""
    if not request.user.is_staff:
        return redirect('dashboard')
        
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    from accounts.models import Payment
    
    # Get current time and the start of today for proper calendar filtering
    now = timezone.now()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Boundaries for filtering
    seven_days_ago = start_of_today - timedelta(days=6)  # Include today + past 6 days
    thirty_days_ago = start_of_today - timedelta(days=29)
    one_year_ago = start_of_today - timedelta(days=364)
    
    # Revenue Totals (Always use 'Paid' status)
    weekly_rev = Payment.objects.filter(date__gte=seven_days_ago, status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_rev = Payment.objects.filter(date__gte=thirty_days_ago, status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    yearly_rev = Payment.objects.filter(date__gte=one_year_ago, status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_rev = Payment.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Period Filtering for Ledger
    period = request.GET.get('period', 'all')
    # Filter by 'Paid' status as well to match the revenue cards
    recent_payments = Payment.objects.select_related('complaint').filter(status='Paid')
    
    period_label = "All Registered Payments"
    if period == 'weekly':
        recent_payments = recent_payments.filter(date__gte=seven_days_ago)
        period_label = "Last 7 Days Payments"
    elif period == 'monthly':
        recent_payments = recent_payments.filter(date__gte=thirty_days_ago)
        period_label = "Last 30 Days Payments"
    elif period == 'yearly':
        recent_payments = recent_payments.filter(date__gte=one_year_ago)
        period_label = "Last 365 Days Payments"
        
    recent_payments = recent_payments.order_by('-date')[:100]
    
    context = {
        'weekly_revenue': weekly_rev,
        'monthly_revenue': monthly_rev,
        'yearly_revenue': yearly_rev,
        'total_revenue': total_rev,
        'recent_payments': recent_payments,
        'current_period': period,
        'period_label': period_label,
    }
    return render(request, 'accounts/admin/admin_wallet.html', context)

@login_required
def staff_management(request):
    if not request.user.is_staff: return redirect('dashboard')
    staff = Staff.objects.all()

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            role = request.POST.get('role')
            name = request.POST['name']
            email = request.POST.get('email')
            if not email and role in ['Driver', 'Worker']:
                import re
                cleaned = re.sub(r'\s*\d+\s*$', '', name)
                cleaned = cleaned.strip().lower()
                cleaned = re.sub(r'[^a-z0-9\s.]', '', cleaned)
                cleaned = re.sub(r'[\s.]+', '.', cleaned)
                if not cleaned:
                    cleaned = role.lower()
                email = f"{cleaned}@example.com"

            s = Staff.objects.create(
                name=name,
                email=email,
                phone=request.POST['phone'],
                cnic=request.POST.get('cnic'),
                address=request.POST.get('address'),
                role=role,
                area=request.POST['area'],
                salary=request.POST.get('salary') or 0
            )
            
            role = s.role
            if role == 'Driver':
                DriverDetail.objects.create(
                    staff=s,
                    dob=request.POST.get('dob') or None,
                    license_number=request.POST.get('license_number'),
                    license_expiry=request.POST.get('license_expiry') or None,
                    license_category=request.POST.get('license_category'),
                    vehicle_assignment=request.POST.get('vehicle_assignment'),
                    plate_number=request.POST.get('plate_number'),
                    experience_years=request.POST.get('experience_years') or None
                )
            elif role == 'Operator':
                OperatorDetail.objects.create(
                    staff=s,
                    operator_id=request.POST.get('operator_id'),
                    shift_assignment=request.POST.get('shift_assignment'),
                    operational_qualification=request.POST.get('operational_qualification'),
                    experience_years=request.POST.get('experience_years_op') or None,
                    certifications=request.POST.get('certifications')
                )
            elif role == 'Supervisor':
                SupervisorDetail.objects.create(
                    staff=s,
                    supervisor_id=request.POST.get('supervisor_id'),
                    department_zone=request.POST.get('department_zone'),
                    management_experience=request.POST.get('management_experience') or None,
                    staff_supervised=request.POST.get('staff_supervised') or None,
                    education_level=request.POST.get('education_level'),
                    supervisory_certification=request.POST.get('supervisory_certification'),
                    key_responsibilities=request.POST.get('key_responsibilities')
                )
            elif role == 'Worker':
                WorkerDetail.objects.create(
                    staff=s,
                    age=request.POST.get('age') or None,
                    duties=request.POST.get('duties'),
                    duty_time=request.POST.get('duty_time')
                )

            messages.success(request, "Staff member added.")
        elif action == 'edit':
            sid = request.POST.get('id')
            s = Staff.objects.get(id=sid)
            s.name = request.POST['name']
            role = request.POST['role']
            email = request.POST.get('email')
            if not email and role in ['Driver', 'Worker']:
                import re
                cleaned = re.sub(r'\s*\d+\s*$', '', s.name)
                cleaned = cleaned.strip().lower()
                cleaned = re.sub(r'[^a-z0-9\s.]', '', cleaned)
                cleaned = re.sub(r'[\s.]+', '.', cleaned)
                if not cleaned:
                    cleaned = role.lower()
                email = f"{cleaned}@example.com"
            s.email = email
            s.phone = request.POST['phone']
            s.cnic = request.POST.get('cnic')
            s.address = request.POST.get('address')
            s.role = role
            s.area = request.POST['area']
            s.salary = request.POST.get('salary') or 0
            s.save()

            role = s.role
            if role == 'Driver':
                detail, _ = DriverDetail.objects.get_or_create(staff=s)
                detail.dob = request.POST.get('dob') or None
                detail.license_number = request.POST.get('license_number')
                detail.license_expiry = request.POST.get('license_expiry') or None
                detail.license_category = request.POST.get('license_category')
                detail.vehicle_assignment = request.POST.get('vehicle_assignment')
                detail.plate_number = request.POST.get('plate_number')
                detail.experience_years = request.POST.get('experience_years') or None
                detail.save()
            elif role == 'Operator':
                detail, _ = OperatorDetail.objects.get_or_create(staff=s)
                detail.operator_id = request.POST.get('operator_id')
                detail.shift_assignment = request.POST.get('shift_assignment')
                detail.operational_qualification = request.POST.get('operational_qualification')
                detail.experience_years = request.POST.get('experience_years_op') or None
                detail.certifications = request.POST.get('certifications')
                detail.save()
            elif role == 'Supervisor':
                detail, _ = SupervisorDetail.objects.get_or_create(staff=s)
                detail.supervisor_id = request.POST.get('supervisor_id')
                detail.department_zone = request.POST.get('department_zone')
                detail.management_experience = request.POST.get('management_experience') or None
                detail.staff_supervised = request.POST.get('staff_supervised') or None
                detail.education_level = request.POST.get('education_level')
                detail.supervisory_certification = request.POST.get('supervisory_certification')
                detail.key_responsibilities = request.POST.get('key_responsibilities')
                detail.save()
            elif role == 'Worker':
                detail, _ = WorkerDetail.objects.get_or_create(staff=s)
                detail.age = request.POST.get('age') or None
                detail.duties = request.POST.get('duties')
                detail.duty_time = request.POST.get('duty_time')
                detail.save()

            messages.success(request, "Staff details updated.")


        elif action == 'delete':
            sid = request.POST.get('id')
            Staff.objects.filter(id=sid).delete()
            messages.warning(request, "Staff member removed.")
        return redirect('staff')

    return render(request, 'accounts/admin/staff.html', {'staff': staff})


@login_required
def complaints(request):
    if not request.user.is_staff:
        messages.error(request, "Access Denied: Administrative permissions required.")
        return redirect('dashboard')
    data = Complaint.objects.filter(payment_status=True).order_by('id')
    staff = Staff.objects.filter(role__in=['Supervisor', 'Operator'])

    return render(request, 'accounts/admin/complaints.html', {
        'complaints': data,
        'staff': staff
    })

@login_required
def update_complaint(request, id):
    if not request.user.is_staff:
        messages.error(request, "Access Denied: Administrative permissions required.")
        return redirect('dashboard')
    complaint = Complaint.objects.get(id=id)
    if complaint.status == 'Completed':
        messages.error(request, "Cannot update complaint. This complaint has already been completed.")
        return redirect('complaints')
    if request.method == "POST":
        staff_id = request.POST.get('staff')
        status = request.POST.get('status')
        after_image = request.FILES.get('after_image')

        old_status = complaint.status

        # Validate status transitions
        if status:
            status_lower = status.lower()
            old_status_lower = old_status.lower() if old_status else ""
            
            if old_status_lower == "completed" and status_lower in ["in progress", "verified", "pending"]:
                messages.error(request, f"Status cannot be changed from 'Completed' to '{status}'.")
                return redirect('complaints')
            elif old_status_lower == "in progress" and status_lower in ["verified", "pending"]:
                messages.error(request, f"Status cannot be changed from 'In Progress' to '{status}'.")
                return redirect('complaints')
            elif old_status_lower == "verified" and status_lower in ["pending"]:
                messages.error(request, f"Status cannot be changed from 'Verified' to '{status}'.")
                return redirect('complaints')

        # If staff is not assigned yet, and no staff_id is provided in the post
        if not complaint.assigned_to and not staff_id:
            messages.error(request, "You must assign a staff member before updating this complaint.")
            return redirect('complaints')

        # If transitioning to "In Progress", ensure a vehicle is assigned under Fleet Tracker
        if status == 'In Progress':
            has_vehicle = Vehicle.objects.filter(current_complaint=complaint).exists()
            if not has_vehicle:
                messages.info(request, "A vehicle must be assigned under Fleet Tracker before setting the status to 'In Progress'. Please register/assign a vehicle here.")
                return redirect(f"/fleet/admin/?assign_complaint={complaint.id}")

        # If transitioning to "Completed", ensure the assigned vehicle's status is "Completed"
        if status == 'Completed':
            vehicle = Vehicle.objects.filter(current_complaint=complaint).first()
            if not vehicle and complaint.assigned_to:
                vehicle = Vehicle.objects.filter(assigned_driver=complaint.assigned_to).first()

            if not vehicle:
                messages.error(request, "Cannot complete complaint. No vehicle is assigned to this complaint.")
                return redirect('complaints')

            if vehicle.status != 'Completed':
                messages.error(request, f"Cannot complete complaint. The assigned vehicle ({vehicle.vehicle_id})'s status must first be set to 'Completed' in Fleet Admin.")
                return redirect('complaints')

        if staff_id:
            complaint.assigned_to = Staff.objects.get(id=staff_id)
        if status:
            complaint.status = status
        if after_image:
            complaint.after_image = after_image
            
        complaint.save()

        if status and status != old_status:
            desc = f"Status updated to {status}."
            if status == "Completed":
                desc = "Work has been completed by the assigned team."
            elif status == "Verified":
                desc = "Complaint has been verified by the administration."
            elif status == "In Progress":
                desc = "Work has started on your complaint."
            
            ComplaintTimeline.objects.create(
                complaint=complaint,
                status=status,
                description=desc
            )
            messages.success(request, f"Complaint {complaint.complaint_id} status updated to {status}.")
            
    return redirect('complaints')

@login_required
def delete_complaint_admin(request, id):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Access Denied: Administrative permissions required.'}, status=403)
    
    try:
        complaint = Complaint.objects.get(id=id)
        complaint_id = complaint.complaint_id
        complaint.delete()
        return JsonResponse({'status': 'success', 'message': f'Complaint {complaint_id} has been removed from the system.'})
    except Complaint.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Complaint not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required(login_url='login')
def submit_feedback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            rating = int(data.get('rating', 0))
            comment = data.get('comment', '').strip()
            # Support 'message' key from legacy tracking page feedback form
            review = data.get('review', data.get('message', '')).strip()
            
            # Validation
            if not (1 <= rating <= 5):
                return JsonResponse({'status': 'error', 'message': 'Rating must be between 1 and 5 stars.'}, status=400)
            
            if not comment and not review:
                return JsonResponse({'status': 'error', 'message': 'Please provide a comment or a review.'}, status=400)

            # Removed Duplicate Prevention as requested - user can now submit multiple reviews
            
            Feedback.objects.create(
                user=request.user,
                rating=rating,
                comment=comment,
                review=review
            )
            return JsonResponse({'status': 'success', 'message': '✅ Thank you! Your feedback has been submitted.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required(login_url='login')
def zone_management_view(request):
    return render(request, 'accounts/zone_management.html')

@login_required
def admin_zone_management(request):
    """
    Administrative view for managing municipal zones.
    Handles listing, adding, editing, and deleting zones.
    """
    if not request.user.is_staff:
        messages.error(request, "Access Denied: Administrative permissions required.")
        return redirect('dashboard')

    zones = Zone.objects.all().order_by('name')
    # Fetch all staff members for assignment dropdown
    staff_members = User.objects.filter(is_staff=True) # Or you might want to filter by specific roles if you have them

    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                boundary_data = request.POST.get('boundary')
                if boundary_data:
                    boundary = json.loads(boundary_data)
                else:
                    boundary = {} # Fallback
                
                staff_id = request.POST.get('assigned_staff')
                assigned_staff = User.objects.get(id=staff_id) if staff_id else None

                Zone.objects.create(
                    name=request.POST.get('name'),
                    status=request.POST.get('status', 'Clean'),
                    boundary=boundary,
                    assigned_staff=assigned_staff
                )
                messages.success(request, f"Zone '{request.POST.get('name')}' added.")
            except Exception as e:
                messages.error(request, f"Error adding zone: {str(e)}")

        elif action == 'edit':
            try:
                zone_id = request.POST.get('id')
                zone = Zone.objects.get(id=zone_id)
                zone.name = request.POST.get('name')
                zone.status = request.POST.get('status')
                
                boundary_data = request.POST.get('boundary')
                if boundary_data:
                    zone.boundary = json.loads(boundary_data)
                
                staff_id = request.POST.get('assigned_staff')
                zone.assigned_staff = User.objects.get(id=staff_id) if staff_id else None
                
                zone.save()
                messages.success(request, f"Zone '{zone.name}' updated.")
            except Exception as e:
                messages.error(request, f"Error updating zone: {str(e)}")

        elif action == 'delete':
            try:
                zone_id = request.POST.get('id')
                Zone.objects.filter(id=zone_id).delete()
                messages.warning(request, "Zone deleted.")
            except Exception as e:
                messages.error(request, f"Error deleting zone: {str(e)}")

        return redirect('admin_zone_management')

    # Stats for the top bar
    stats = {
        'total': zones.count(),
        'critical': zones.filter(status='Critical').count(),
        'moderate': zones.filter(status='Moderate').count(),
        'clean': zones.filter(status='Clean').count(),
    }

    context = {
        'zones': zones,
        'staff_members': staff_members,
        'stats': stats,
    }
    return render(request, 'accounts/admin/zone_management_admin.html', context)

@login_required(login_url='login')
def vehicle_tracking_view(request):
    # _seed_fleet() # Removed to prevent automatic recreation after deletion
    cid = request.GET.get('complaint_id')
    complaint = None
    vehicle = None
    error = None
    
    if cid:
        try:
            complaint = Complaint.objects.get(complaint_id__iexact=cid, payment_status=True)
            # Try finding vehicle directly linked or via assigned staff
            vehicle = Vehicle.objects.filter(current_complaint=complaint).first()
            if not vehicle and complaint.assigned_to:
                vehicle = Vehicle.objects.filter(assigned_driver=complaint.assigned_to).first()
            
            if not vehicle:
                # Fallback: maybe just find any vehicle in the same area/zone
                vehicle = Vehicle.objects.filter(assigned_zone=complaint.area).first()
                
            if not vehicle:
                error = "No active vehicle is currently dispatched for this complaint."
        except Complaint.DoesNotExist:
            error = "Invalid Tracking ID. Please check your ID and try again."
            
    return render(request, 'accounts/vehicle_tracking.html', {
        'complaint': complaint,
        'tracked_vehicle': vehicle,
        'error': error,
        'search_cid': cid
    })


# --- ANNOUNCEMENTS / ALERTS API ---

@login_required(login_url='login')
def get_announcements(request):
    """Unified Inbox API returning announcements, personal notifications, status updates, and reviews with human-readable timestamps."""
    
    def get_time_str(dt):
        diff = timezone.now() - dt
        if diff.days > 0: return f"{diff.days}d ago"
        if diff.seconds > 3600: return f"{diff.seconds // 3600}h ago"
        if diff.seconds > 60: return f"{diff.seconds // 60}m ago"
        return "Just now"

    try:
        # 1. System Announcements
        announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:15]
        read_ann_ids = AnnouncementRead.objects.filter(user=request.user).values_list('announcement_id', flat=True)
        
        # 2. Personal Notifications
        personal_notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')[:25]
        
        # 3. Personal Complaint Status Updates - Now handled by Notification model in signals.py
        # We no longer pull from ComplaintTimeline here to avoid duplicates.

        
        # Section removed: Community Reviews (Feedback) - Global view
        
        data = []
        
        for ann in announcements:
            data.append({
                'unique_id': f"ann_{ann.id}",
                'id': ann.id,
                'type': 'announcement',
                'title': ann.title,
                'message': ann.message,
                'alert_type': ann.alert_type,
                'created_at': get_time_str(ann.created_at),
                'raw_time': ann.created_at.timestamp(),
                'is_read': ann.id in read_ann_ids
            })
            
        seen_notifications = set()
        for pn in personal_notifications:
            # Create a unique key based on title and message to identify duplicates
            notif_key = f"{pn.title}|{pn.message}"
            if notif_key in seen_notifications:
                continue
            seen_notifications.add(notif_key)
            
            data.append({
                'unique_id': f"notif_{pn.id}",
                'id': pn.id,
                'type': 'personal',
                'title': pn.title,
                'message': pn.message,
                'alert_type': pn.alert_type,
                'created_at': get_time_str(pn.timestamp),
                'raw_time': pn.timestamp.timestamp(),
                'is_read': pn.is_read
            })

            

        
        # Sort everything by raw timestamp descending
        data.sort(key=lambda x: x['raw_time'], reverse=True)
        
        # Identify the latest unread system announcement for the top banner
        latest_alert = next((ann for ann in data if ann['type'] == 'announcement' and not ann['is_read']), None)
        
        return JsonResponse({
            'status': 'success', 
            'announcements': data,
            'latest_alert': latest_alert
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required(login_url='login')
def mark_announcement_read(request, pk):
    """Handle both Announcement and Notification read status."""
    item_type = request.GET.get('type', 'announcement')
    
    if item_type == 'announcement':
        try:
            announcement = Announcement.objects.get(pk=pk)
            AnnouncementRead.objects.get_or_create(user=request.user, announcement=announcement)
            return JsonResponse({'status': 'success'})
        except Announcement.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    elif item_type == 'personal':
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid type'}, status=400)

@login_required(login_url='login')
def mark_all_user_notifications_read(request):
    """Marks all personal notifications and administrative updates as read for the user."""
    # 1. Mark personal notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    # 2. Mark announcements as read (using AnnouncementRead mapping)
    active_announcements = Announcement.objects.filter(is_active=True)
    for ann in active_announcements:
        AnnouncementRead.objects.get_or_create(user=request.user, announcement=ann)
        
    # 3. For staff, mark admin notifications as read
    if request.user.is_staff:
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
        
    return JsonResponse({'status': 'success'})

@login_required(login_url='login')
def delete_all_user_notifications(request):
    """Deletes all personal notifications for the user and marks announcements as read."""
    # 1. Delete personal notifications
    Notification.objects.filter(user=request.user).delete()
    
    # 2. Mark announcements as read (using AnnouncementRead mapping)
    active_announcements = Announcement.objects.filter(is_active=True)
    for ann in active_announcements:
        AnnouncementRead.objects.get_or_create(user=request.user, announcement=ann)
        
    return JsonResponse({'status': 'success'})

@login_required(login_url='login')
def delete_notification(request, pk):
    """Deletes a specific personal notification."""
    try:
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.delete()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)

# --- ZONE MANAGEMENT API ---

@login_required(login_url='login')
def notifications_view(request):
    """Full-page Unified Inbox view."""
    return render(request, 'accounts/notifications.html')

@login_required(login_url='login')
def get_zones(request):
    zones = Zone.objects.all()
    features = []
    
    for zone in zones:
        # Simulate some data for graphs since we don't have direct FK relations
        active = random.randint(1, 15)
        resolved = random.randint(10, 50)
        
        features.append({
            "type": "Feature",
            "id": zone.id,
            "properties": {
                "name": zone.name,
                "status": zone.status,
                "total_complaints": zone.complaint_count,
                "active_complaints": active,
                "resolved_complaints": resolved,
                "staff": zone.assigned_staff.username if zone.assigned_staff else "Not Assigned",
                "color": "#10b981" if zone.status == 'Clean' else "#f59e0b" if zone.status == 'Moderate' else "#ef4444"
            },
            "geometry": zone.boundary if isinstance(zone.boundary, dict) and zone.boundary.get("type") else None
        })
        
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

@login_required(login_url='login')
def detect_zone(request):
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        
        # Simple point-in-polygon check or spatial query
        # Since we use JSONField, we can implement a basic ray-casting algorithm or just return the closest central zone
        # For professional results, we'll return the zone that matches the area string if provided, 
        # or just the first matching polygon.
        
        # Simplified for now: return all zones and let frontend handle high-precision detection
        return JsonResponse({'status': 'success', 'lat': lat, 'lng': lng})
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)


# ============================================================
# FLEET MANAGEMENT — Seed Data & Simulation
# ============================================================

FLEET_SEED_DATA = [
    {'vehicle_id': 'GT-101', 'vehicle_type': 'Garbage issue',      'driver_name': 'Ahmed Khan',     'driver_phone': '0321-1234567', 'assigned_zone': 'Model Town',  'base_lat': 32.5736, 'base_lng': 74.0790, 'sim_phase': 0.00, 'status': 'Active',  'plate_number': 'GJT-451'},
    {'vehicle_id': 'GT-102', 'vehicle_type': 'Water issue',        'driver_name': 'Sajid Malik',    'driver_phone': '0300-9876543', 'assigned_zone': 'G.T. Road',   'base_lat': 32.5651, 'base_lng': 74.0843, 'sim_phase': 0.78, 'status': 'In Transit',  'plate_number': 'GJT-872'},
    {'vehicle_id': 'GT-103', 'vehicle_type': 'Street light issue', 'driver_name': 'Irfan Sheikh',   'driver_phone': '0345-5556666', 'assigned_zone': 'Bhimber Road','base_lat': 32.5510, 'base_lng': 74.0621, 'sim_phase': 1.57, 'status': 'Idle',    'plate_number': 'GJT-339'},
    {'vehicle_id': 'GT-104', 'vehicle_type': 'Street cleaning',    'driver_name': 'Zahid Javed',    'driver_phone': '0311-2223333', 'assigned_zone': 'Shahdowla',   'base_lat': 32.5820, 'base_lng': 74.0912, 'sim_phase': 2.36, 'status': 'Arrived',  'plate_number': 'GJT-104'},
    {'vehicle_id': 'GT-105', 'vehicle_type': 'Garbage issue',      'driver_name': 'Imran Ali',      'driver_phone': '0333-7778888', 'assigned_zone': 'Dinga Road',  'base_lat': 32.5470, 'base_lng': 74.1215, 'sim_phase': 3.14, 'status': 'Work in Progress',  'plate_number': 'GJT-605'},
    {'vehicle_id': 'GT-106', 'vehicle_type': 'Water issue',        'driver_name': 'Usman Raza',     'driver_phone': '0312-4445555', 'assigned_zone': 'Civil Lines', 'base_lat': 32.5762, 'base_lng': 74.0778, 'sim_phase': 3.93, 'status': 'Idle',    'plate_number': 'GJT-216'},
    {'vehicle_id': 'GT-107', 'vehicle_type': 'Street light issue', 'driver_name': 'Bilal Ahmad',    'driver_phone': '0322-6667777', 'assigned_zone': 'Kanjwani',    'base_lat': 32.5680, 'base_lng': 74.0550, 'sim_phase': 4.71, 'status': 'Delayed',  'plate_number': 'GJT-717'},
    {'vehicle_id': 'GT-108', 'vehicle_type': 'Street cleaning',    'driver_name': 'Tariq Mehmood',  'driver_phone': '0331-8889999', 'assigned_zone': 'Gondal Road', 'base_lat': 32.5923, 'base_lng': 74.0710, 'sim_phase': 5.50, 'status': 'Offline', 'plate_number': 'GJT-308'},
    {'vehicle_id': 'GT-109', 'vehicle_type': 'Drainage issue',     'driver_name': 'Mubeen Shah',    'driver_phone': '0300-1112222', 'assigned_zone': 'Fawara Chowk','base_lat': 32.5700, 'base_lng': 74.0700, 'sim_phase': 1.23, 'status': 'Idle',    'plate_number': 'GJT-909'},
]

def _seed_fleet():
    """Auto-seed fleet vehicles if none exist in the database."""
    if Vehicle.objects.count() == 0:
        for d in FLEET_SEED_DATA:
            Vehicle.objects.create(**d)


def _sim_pos(v):
    """Compute a smooth simulated GPS position for a vehicle based on current time."""
    t = time.time()
    moving_statuses = ['Active', 'In Transit', 'Work in Progress', 'Delayed']
    if v.status in moving_statuses:
        # Faster simulation for In Transit, slower for others
        speed_mult = 0.025 if v.status == 'In Transit' else 0.01
        lat = v.base_lat + math.sin(t * speed_mult + v.sim_phase) * 0.004
        lng = v.base_lng + math.cos(t * speed_mult + v.sim_phase) * 0.006
        speed = round(20.0 + math.sin(t * 0.08 + v.sim_phase) * 10.0, 1)
        if v.status == 'Delayed': speed *= 0.4
    elif v.status in ['Idle', 'Arrived']:
        lat = v.base_lat + math.sin(v.sim_phase) * 0.0005
        lng = v.base_lng + math.cos(v.sim_phase) * 0.0005
        speed = 0.0
    else:  # Offline, Out of Service, Completed, Cancelled
        lat = v.base_lat
        lng = v.base_lng
        speed = 0.0
    return round(lat, 6), round(lng, 6), max(0.0, speed)


# ============================================================
# FLEET API VIEWS
# ============================================================

@login_required(login_url='login')
def api_vehicles_list(request):
    """Return all active vehicles with their current simulated positions."""
    # _seed_fleet()
    vehicle_data = []
    for v in Vehicle.objects.filter(is_active=True).order_by('vehicle_id'):
        lat, lng, spd = _sim_pos(v)
        vehicle_data.append({
            'id': v.id,
            'vehicle_id': v.vehicle_id,
            'vehicle_type': v.vehicle_type,
            'driver_name': v.driver_name,
            'driver_phone': v.driver_phone,
            'assigned_zone': v.assigned_zone,
            'current_complaint_id': v.current_complaint.complaint_id if v.current_complaint else None,
            'current_complaint_area': v.current_complaint.area if v.current_complaint else None,
            'status': v.status,
            'plate_number': v.plate_number,
            'lat': lat,
            'lng': lng,
            'speed': spd,
            'base_lat': v.base_lat,
            'base_lng': v.base_lng,
            'source_name': v.source_name,
            'sim_phase': v.sim_phase,
            'approaching_time': v.approaching_time,
            'assign_time': v.assign_time.strftime('%H:%M') if v.assign_time else None,
        })
    qs = Vehicle.objects.all()
    stats = {
        'active': qs.filter(status='Active').count(),
        'transit': qs.filter(status='In Transit').count(),
        'work': qs.filter(status='Work in Progress').count(),
        'idle': qs.filter(status='Idle').count(),
        'offline': qs.filter(status='Offline').count(),
        'total': qs.count(),
    }
    return JsonResponse({'vehicles': vehicle_data, 'stats': stats})


@login_required(login_url='login')
def api_vehicle_history(request, pk):
    """Return the last 30 simulated GPS points for route replay (last ~15 minutes)."""
    try:
        v = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return JsonResponse({'error': 'Vehicle not found'}, status=404)

    now = time.time()
    points = []
    if v.status != 'Offline':
        for i in range(30, -1, -1):
            t_past = now - i * 30  # one point every 30 seconds
            lat = v.base_lat + math.sin(t_past * 0.025 + v.sim_phase) * 0.004
            lng = v.base_lng + math.cos(t_past * 0.025 + v.sim_phase) * 0.006
            points.append([round(lat, 6), round(lng, 6)])

    return JsonResponse({'vehicle_id': v.vehicle_id, 'history': points})


# ============================================================
# FLEET ADMIN VIEWS
# ============================================================

@login_required(login_url='login')
@login_required
def fleet_admin_view(request):
    """Admin fleet management dashboard."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff permissions required.')
        return redirect('dashboard')
    # _seed_fleet()
    vehicles = Vehicle.objects.all().order_by('-created_at')
    zones = Zone.objects.all()
    supervisors = Staff.objects.filter(role='Supervisor')
    drivers = Staff.objects.filter(role='Driver').select_related('driver_detail')
    
    # If the user is a supervisor, filter the data to their assigned zone
    is_supervisor = False
    assigned_zone_obj = None
    if not request.user.is_superuser and hasattr(request.user, 'staff_profile'):
        staff_profile = request.user.staff_profile
        if staff_profile.role == 'Supervisor':
            is_supervisor = True
            assigned_zone_obj = staff_profile.assigned_zone
            if assigned_zone_obj:
                vehicles = vehicles.filter(assigned_zone=assigned_zone_obj.name)

    # Calculate counts for charts
    v_types = {
        'garbage': vehicles.filter(vehicle_type='Garbage issue').count(),
        'water': vehicles.filter(vehicle_type='Water issue').count(),
        'service': vehicles.filter(vehicle_type='Street light issue').count(),
        'sweeper': vehicles.filter(vehicle_type='Street cleaning').count(),
        'drainage': vehicles.filter(vehicle_type='Drainage issue').count(),
    }

    context = {
        'vehicles': vehicles,
        'zones': zones,
        'active_count': vehicles.filter(status='Active').count(),
        'transit_count': vehicles.filter(status='In Transit').count(),
        'idle_count': vehicles.filter(status='Idle').count(),
        'offline_count': vehicles.filter(status='Offline').count(),
        'delayed_count': vehicles.filter(status='Delayed').count(),
        'arrived_count': vehicles.filter(status='Arrived').count(),
        'working_count': vehicles.filter(status='Work in Progress').count(),
        'finished_count': vehicles.filter(status='Completed').count(),
        'total_count': vehicles.count(),
        'v_types': v_types,
        'supervisors': supervisors,
        'drivers': drivers,
        'all_complaints': Complaint.objects.filter(payment_status=True, tracked_vehicle__isnull=True).order_by('-created_at'),
        'is_supervisor': is_supervisor,
        'assigned_zone_obj': assigned_zone_obj,
        'all_users': User.objects.all(),
        'gujrat_areas': GUJRAT_AREAS,
        'categories': ServiceCategory.objects.all(),
    }
    return render(request, 'accounts/admin/fleet_management.html', context)

@login_required(login_url='login')
def assign_staff_area(request):
    """Assign a supervisor to a specific zone."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        zone_id = request.POST.get('zone_id')
        user_id = request.POST.get('user_id')
        
        try:
            staff = Staff.objects.get(id=staff_id)
            if zone_id:
                staff.assigned_zone = Zone.objects.get(id=zone_id)
                staff.area = staff.assigned_zone.name # Sync with legacy field
            else:
                staff.assigned_zone = None
            
            if user_id:
                staff.user = User.objects.get(id=user_id)
            
            staff.save()
            messages.success(request, f'Area assignment updated for {staff.name}.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            
    return redirect('fleet_admin')


@login_required(login_url='login')
def fleet_add_vehicle(request):
    """Add a new vehicle to the fleet."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    if request.method == 'POST':
        try:
            import random as _rnd
            driver_id = request.POST.get('assigned_driver')
            driver = Staff.objects.get(id=driver_id) if driver_id else None
            
            salary = request.POST.get('salary')
            if driver and salary:
                driver.salary = salary
                driver.save()

            Vehicle.objects.create(
                vehicle_id=request.POST['vehicle_id'].strip().upper(),
                vehicle_type=request.POST['vehicle_type'],
                driver_name=driver.name if driver else request.POST['driver_name'].strip(),
                driver_phone=driver.phone if driver else request.POST.get('driver_phone', '').strip(),
                assigned_driver=driver,
                current_complaint=Complaint.objects.filter(id=request.POST.get('current_complaint'), payment_status=True).first() if request.POST.get('current_complaint') else None,
                assigned_zone=request.POST.get('assigned_zone', '').strip(),
                status=request.POST.get('status', 'Idle'),
                plate_number=request.POST.get('plate_number', '').strip(),
                base_lat=float(request.POST.get('base_lat', 32.5736)),
                base_lng=float(request.POST.get('base_lng', 74.0790)),
                source_name=request.POST.get('source_name', 'Main Depot').strip(),
                sim_phase=round(_rnd.uniform(0, 6.28), 2),
                latitude=float(request.POST.get('latitude')) if request.POST.get('latitude') else None,
                longitude=float(request.POST.get('longitude')) if request.POST.get('longitude') else None,
                assign_date=request.POST.get('assign_date') or None,
                assign_time=request.POST.get('assign_time') or None,
                estimating_time=request.POST.get('estimating_time', '').strip(),
                approaching_time=request.POST.get('approaching_time', '').strip(),
            )
            messages.success(request, 'Vehicle added!')
        except Exception as e:
            messages.error(request, f'Error adding vehicle: {e}')
    return redirect('fleet_admin')


@login_required(login_url='login')
def fleet_edit_vehicle(request, pk):
    """Edit an existing vehicle's details."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    try:
        vehicle = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        messages.error(request, 'Vehicle not found.')
        return redirect('fleet_admin')
    if request.method == 'POST':
        try:
            vehicle.vehicle_id = request.POST.get('vehicle_id', vehicle.vehicle_id).strip().upper()
            vehicle.vehicle_type = request.POST.get('vehicle_type', vehicle.vehicle_type)
            
            driver_id = request.POST.get('assigned_driver')
            if driver_id:
                driver = Staff.objects.get(id=driver_id)
                vehicle.assigned_driver = driver
                vehicle.driver_name = driver.name
                vehicle.driver_phone = driver.phone
                
                salary = request.POST.get('salary')
                if salary:
                    driver.salary = salary
                    driver.save()
            else:
                vehicle.driver_name = request.POST.get('driver_name', vehicle.driver_name).strip()
                vehicle.driver_phone = request.POST.get('driver_phone', vehicle.driver_phone).strip()

            vehicle.assigned_zone = request.POST.get('assigned_zone', vehicle.assigned_zone).strip()
            
            curr_comp = request.POST.get('current_complaint')
            if curr_comp:
                try:
                    vehicle.current_complaint = Complaint.objects.filter(id=curr_comp, payment_status=True).first()
                except:
                    vehicle.current_complaint = None
            elif 'current_complaint' in request.POST:
                vehicle.current_complaint = None

            vehicle.status = request.POST.get('status', vehicle.status)
            vehicle.plate_number = request.POST.get('plate_number', vehicle.plate_number).strip()
            
            try:
                if request.POST.get('base_lat'): vehicle.base_lat = float(request.POST['base_lat'])
                if request.POST.get('base_lng'): vehicle.base_lng = float(request.POST['base_lng'])
                if request.POST.get('latitude'): vehicle.latitude = float(request.POST['latitude'])
                if request.POST.get('longitude'): vehicle.longitude = float(request.POST['longitude'])
            except:
                pass

            vehicle.source_name = request.POST.get('source_name', vehicle.source_name).strip()
            vehicle.assign_date = request.POST.get('assign_date') or None
            vehicle.assign_time = request.POST.get('assign_time') or None
            vehicle.estimating_time = request.POST.get('estimating_time', '').strip()
            vehicle.approaching_time = request.POST.get('approaching_time', '').strip()
            vehicle.save()
            messages.success(request, f'Vehicle {vehicle.vehicle_id} updated!')
        except Exception as e:
            messages.error(request, f'Error updating vehicle: {e}')
    return redirect('fleet_admin')


@login_required(login_url='login')
def fleet_delete_vehicle(request, pk):
    """Delete a vehicle from the fleet. Supports AJAX to avoid full page refresh."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    if request.method == 'POST':
        try:
            vehicle = Vehicle.objects.get(pk=pk)
            vid = vehicle.vehicle_id
            vehicle.delete()
            # If AJAX request, return JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'deleted',
                    'vehicle_id': vid,
                })
            messages.warning(request, f'Vehicle {vid} deleted.')
        except Vehicle.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'error': 'Vehicle not found.'}, status=404)
            messages.error(request, 'Vehicle not found.')
    return redirect('fleet_admin')

@login_required(login_url='login')
def fleet_upload_proof(request, pk):
    """View to allow admins to upload completion proof (image/video) for a complaint linked to a vehicle."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            vehicle = Vehicle.objects.get(pk=pk)
            complaint = vehicle.current_complaint
            if not complaint:
                messages.error(request, 'No complaint linked to this vehicle.')
                return redirect('fleet_admin')
            
            proof_image = request.FILES.get('proof_image')
            proof_video = request.FILES.get('proof_video')
            
            if proof_image:
                complaint.proof_image = proof_image
            if proof_video:
                complaint.proof_video = proof_video
            
            # Update status
            complaint.status = 'Completed'
            vehicle.status = 'Completed'
            
            # Timeline entry
            ComplaintTimeline.objects.create(
                complaint=complaint,
                status='Completed',
                description='Admin uploaded completion proof. Task resolved successfully.'
            )
                
            complaint.save()
            vehicle.save()
            
            messages.success(request, 'Proof uploaded and status updated to Completed.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            
    return redirect('fleet_admin')


# ============================================================
# SERVICE SCHEDULING - ADMIN VIEWS
# ============================================================

def _seed_services():
    """Seed or update default service categories."""
    if ServicePaymentSetting.objects.exists():
        return
        
    services = [
        {'name': 'Garbage Pickup', 'base_price': 150.00, 'urgent_price': 250.00, 'advance_booking_fee': 50.00, 'icon': 'bi-trash', 'description': 'Door-to-door and container collection.'},
        {'name': 'Street Cleaning', 'base_price': 200.00, 'urgent_price': 350.00, 'advance_booking_fee': 75.00, 'icon': 'bi-broom', 'description': 'Sweeping and sanitation.'},
        {'name': 'Drainage', 'base_price': 400.00, 'urgent_price': 600.00, 'advance_booking_fee': 100.00, 'icon': 'bi-water', 'description': 'Maintenance and desilting.'},
        {'name': 'Water Supply', 'base_price': 350.00, 'urgent_price': 500.00, 'advance_booking_fee': 80.00, 'icon': 'bi-droplet', 'description': 'Pumping timings and pressure updates.'},
    ]
    
    # Create or Update existing to match current names
    for s in services:
        obj, created = ServiceCategory.objects.get_or_create(name=s['name'])
        if created:
            obj.base_price = s['base_price']
            obj.urgent_price = s['urgent_price']
            obj.advance_booking_fee = s['advance_booking_fee']
            obj.icon = s['icon']
            obj.description = s['description']
            obj.save()

    # Clean up old names if they exist
    old_names = ['Garbage Pickup', 'Drainage Cleaning', 'Water Services', 'Garbage Issues', 'Drainage Issues', 'Water Issues']
    ServiceCategory.objects.filter(name__in=old_names).exclude(name__in=[s['name'] for s in services]).delete()
    
    if ServicePaymentSetting.objects.count() == 0:
        ServicePaymentSetting.objects.create(gateway_name="Stripe", is_active=True)

def _seed_municipal_schedules():
    """Seed demo municipal schedules if none exist."""
    if ServicePaymentSetting.objects.exists() and MunicipalServiceSchedule.objects.exists():
        return
        
    _seed_services()  # Ensure categories exist first
    if MunicipalServiceSchedule.objects.count() == 0:
        garbage_svc = ServiceCategory.objects.filter(name='Garbage Pickup').first()
        water_svc = ServiceCategory.objects.filter(name='Water Supply').first()
        street_svc = ServiceCategory.objects.filter(name='Street Cleaning').first()
        
        if garbage_svc:
            MunicipalServiceSchedule.objects.create(
                service=garbage_svc,
                area_name="Fawara Chowk",
                union_council="",
                start_time=dt_time(8, 0),
                end_time=dt_time(12, 0),
                frequency="Daily",
                admin_notes="Main collection point nearby."
            )
            MunicipalServiceSchedule.objects.create(
                service=garbage_svc,
                area_name="Jalalpur Jattan",
                union_council="",
                start_time=dt_time(9, 30),
                end_time=dt_time(13, 0),
                frequency="Weekly",
                day_of_week="Monday",
                admin_notes="Container collection only."
            )
        
        if water_svc:
            MunicipalServiceSchedule.objects.create(
                service=water_svc,
                area_name="Model Town",
                union_council="",
                start_time=dt_time(6, 0),
                end_time=dt_time(9, 0),
                frequency="Daily",
                admin_notes="High pressure pumping."
            )

@login_required
def service_admin_view(request):
    """Main administrative dashboard for the unified Service & Schedule Suite."""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    _seed_services()
    _seed_municipal_schedules()
    
    context = {
        'categories': ServiceCategory.objects.all(),
        'payment_settings': ServicePaymentSetting.objects.first(),
        'staff_members': Staff.objects.all(),
        'schedules': MunicipalServiceSchedule.objects.all().order_by('area_name'),
        'alerts': ScheduleAlert.objects.all().order_by('-created_at'),
        'holidays': HolidayConfig.objects.all().order_by('-date'),
    }
    
    return render(request, 'accounts/admin/service_suite.html', context)

@login_required
def manage_service_categories(request):
    """Handle CRUD for service categories."""
    if not request.user.is_staff: return redirect('dashboard')
    
    if request.method == "POST":
        action = request.POST.get('action')
        name = request.POST.get('name')
        price = request.POST.get('base_price')
        urgent_price = request.POST.get('urgent_price', 0)
        advance_fee = request.POST.get('advance_booking_fee', 0)
        multiplier = request.POST.get('urgency_multiplier', 1.5)
        icon = request.POST.get('icon', 'bi-gear')
        desc = request.POST.get('description', '')
        
        if action == 'add':
            ServiceCategory.objects.create(
                name=name, 
                base_price=price, 
                urgent_price=urgent_price,
                advance_booking_fee=advance_fee,
                urgency_multiplier=multiplier, 
                icon=icon, 
                description=desc
            )
            messages.success(request, f"Service category '{name}' added.")
        elif action == 'edit':
            cid = request.POST.get('id')
            cat = ServiceCategory.objects.get(id=cid)
            cat.name, cat.base_price, cat.urgent_price, cat.advance_booking_fee, cat.urgency_multiplier, cat.icon, cat.description = name, price, urgent_price, advance_fee, multiplier, icon, desc
            cat.save()
            messages.success(request, f"Service category '{name}' updated.")
        elif action == 'delete':
            cid = request.POST.get('id')
            ServiceCategory.objects.filter(id=cid).delete()
            messages.warning(request, "Service category deleted.")
            
    return redirect('service_admin')

@login_required
def manage_bookings_admin(request):
    """Handle CRUD and status updates for bookings."""
    if not request.user.is_staff: return redirect('dashboard')
    
    if request.method == "POST":
        action = request.POST.get('action')
        bid = request.POST.get('id')
        booking = ServiceBooking.objects.get(id=bid)
        
        if action == 'update_status':
            booking.status = request.POST.get('status')
            staff_id = request.POST.get('assigned_staff')
            if staff_id:
                booking.assigned_staff = Staff.objects.get(id=staff_id)
            booking.save()
            messages.success(request, f"Booking status updated to {booking.status}.")
        elif action == 'delete':
            booking.delete()
            messages.warning(request, "Booking deleted.")
        elif action == 'edit':
            booking.scheduled_date = request.POST.get('date')
            booking.address = request.POST.get('address')
            booking.total_cost = request.POST.get('cost')
            booking.save()
            messages.success(request, "Booking details updated.")
            
    return redirect('service_admin')

@login_required
def update_payment_settings(request):
    """Update gateway credentials."""
    if not request.user.is_staff: return redirect('dashboard')
    
    if request.method == "POST":
        settings = ServicePaymentSetting.objects.first()
        settings.merchant_id = request.POST.get('merchant_id')
        settings.merchant_key = request.POST.get('merchant_key')
        settings.is_active = 'is_active' in request.POST
        settings.save()
        messages.success(request, "Payment settings updated.")
        
    return redirect('service_admin')

# ============================================================
# SERVICE SCHEDULING - USER VIEWS
# ============================================================

@login_required
def book_service_wizard(request):
    """Multi-step booking wizard for users."""
    _seed_services()
    categories = ServiceCategory.objects.all()
    
    if request.method == "POST":
        try:
            category_id = request.POST.get('service_id')
            urgency = request.POST.get('urgency')
            date = request.POST.get('date')
            address = request.POST.get('address')
            
            svc = ServiceCategory.objects.get(id=category_id)
            is_advance = request.POST.get('is_advance') == 'true'
            
            # Use explicit pricing
            calculated_cost = svc.urgent_price if urgency == 'Urgent' else svc.base_price
            
            # Add advance fee if applicable
            advance_fee = 0
            if is_advance:
                advance_fee = svc.advance_booking_fee
                calculated_cost += advance_fee
                
            booking = ServiceBooking.objects.create(
                user=request.user,
                service=svc,
                urgency=urgency,
                is_advance=is_advance,
                advance_fee_paid=advance_fee,
                scheduled_date=date,
                address=address,
                total_cost=calculated_cost,
                status='Pending'
            )
            
            # Save booking to session for payment flow
            request.session['pending_booking_id'] = booking.id
            return redirect('booking_stripe_checkout')
        except Exception as e:
            messages.error(request, f"Booking Error: {str(e)}")
            
    return render(request, 'accounts/book_service.html', {'categories': categories})

@login_required
def booking_stripe_checkout(request):
    bid = request.session.get('pending_booking_id')
    if not bid: return redirect('book_service')
    
    booking = ServiceBooking.objects.get(id=bid)
    settings = ServicePaymentSetting.objects.first()
    
    if not settings or not settings.is_active:
        messages.error(request, "Electronic payments are currently disabled by the administrator. Please contact support.")
        return redirect('book_service')
        
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pkr',
                    'unit_amount': int(booking.total_cost * 100),
                    'product_data': {
                        'name': f'Service Booking ({booking.service.name})',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('booking_stripe_success')),
            cancel_url=request.build_absolute_uri(reverse('book_service')),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('book_service')

@login_required
def booking_stripe_success(request):
    bid = request.session.get('pending_booking_id')
    if not bid: return redirect('dashboard')
    
    booking = ServiceBooking.objects.get(id=bid)
    booking.payment_status = True
    booking.status = 'Scheduled'
    booking.save()
    
    # Record in Wallet as a Payment Transaction
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    WalletTransaction.objects.create(
        wallet=wallet,
        amount=booking.total_cost,
        transaction_type='Payment',
        description=f"Payment for Service Booking: {booking.service.name}"
    )
    wallet.balance -= booking.total_cost
    wallet.save()
    
    del request.session['pending_booking_id']
    messages.success(request, "Service booked!")
    return render(request, 'accounts/booking_success.html', {'booking': booking})

# --- MUNICIPAL SCHEDULE VIEWS ---

def schedule_public_view(request):
    """Searchable public portal for municipal service schedules."""
    _seed_municipal_schedules()
    today = timezone.now().date()
    now_time = timezone.now().time()
    
    # Check for holiday
    holiday = HolidayConfig.objects.filter(date=today, is_active=True).first()
    
    query = request.GET.get('q', '')
    schedules = MunicipalServiceSchedule.objects.filter(is_active=True)
    
    if query:
        schedules = schedules.filter(
            Q(area_name__icontains=query)
        )
    
    now = timezone.now()
    active_alerts = ScheduleAlert.objects.filter(is_active=True).filter(
        Q(visibility_duration='permanent') |
        Q(visibility_duration='24h', created_at__gte=now - timedelta(hours=24)) |
        Q(visibility_duration='until_resolved', status__in=['active', 'in_progress', 'delayed'])
    ).order_by('-created_at')
    
    # Logic to determine status
    schedule_list = []
    for s in schedules:
        status = "Active"
        if holiday:
            status = "CLOSED / HOLIDAY"
        else:
            # Check for specific "Delayed" status via active alerts
            has_alert = active_alerts.filter(
                Q(area__icontains=s.area_name),
                service=s.service
            ).exists()
            
            if has_alert:
                status = "Delayed"
            elif s.start_time <= now_time <= s.end_time:
                status = "Active"
            elif now_time < s.start_time:
                status = "Upcoming"
            else:
                status = "Completed"
        
        schedule_list.append({
            'data': s,
            'status': status
        })
        
    context = {
        'schedules': schedule_list,
        'holiday': holiday,
        'alerts': active_alerts,
        'query': query
    }
    return render(request, 'accounts/schedule_public.html', context)

@login_required
def admin_schedule_manage(request):
    """Handles POST actions for the Service Suite (schedules, alerts, holidays)."""
    if not request.user.is_staff:
        return redirect('dashboard')
        
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add_schedule':
            MunicipalServiceSchedule.objects.create(
                service_id=request.POST['service_id'],
                area_name=request.POST['area_name'],
                union_council=request.POST.get('union_council', ''),
                start_time=request.POST['start_time'],
                end_time=request.POST['end_time'],
                frequency=request.POST['frequency'],
                day_of_week=request.POST.get('day_of_week'),
                admin_notes=request.POST.get('admin_notes', '')
            )
            messages.success(request, "Schedule added.")
            
        elif action == 'post_alert':
            ScheduleAlert.objects.create(
                area=request.POST['area'],
                service_id=request.POST['service_id'],
                title=request.POST['title'],
                message=request.POST['message'],
                priority=request.POST.get('priority', 'medium'),
                status=request.POST.get('status', 'active'),
                start_date=request.POST.get('start_date') or None,
                end_date=request.POST.get('end_date') or None,
                supervisor_name=request.POST.get('supervisor_name'),
                helpline_number=request.POST.get('helpline_number'),
                response_team_contact=request.POST.get('response_team_contact'),
                visibility_duration=request.POST.get('visibility_duration', 'permanent'),
                is_active=True
            )
            messages.success(request, "Advanced Schedule Alert posted successfully!")
            
        elif action == 'toggle_holiday':
            HolidayConfig.objects.update_or_create(
                date=request.POST['date'],
                defaults={
                    'name': request.POST['name'],
                    'is_active': 'is_active' in request.POST,
                    'special_plan': request.POST.get('special_plan', '')
                }
            )
            messages.success(request, "Holiday configuration updated.")
            
        elif action == 'edit_schedule':
            sid = request.POST.get('id')
            sched = MunicipalServiceSchedule.objects.get(id=sid)
            sched.service_id = request.POST['service_id']
            sched.area_name = request.POST['area_name']
            sched.union_council = request.POST.get('union_council', '')
            sched.start_time = request.POST['start_time']
            sched.end_time = request.POST['end_time']
            sched.frequency = request.POST['frequency']
            sched.day_of_week = request.POST.get('day_of_week')
            sched.admin_notes = request.POST.get('admin_notes', '')
            sched.save()
            messages.success(request, "Schedule updated.")
            
        elif action == 'delete_schedule':
            MunicipalServiceSchedule.objects.filter(id=request.POST.get('id')).delete()
            messages.warning(request, "Schedule deleted.")
            
        elif action == 'delete_alert':
            ScheduleAlert.objects.filter(id=request.POST.get('id')).delete()
            messages.warning(request, "Alert removed.")

        elif action == 'edit_alert':
            aid = request.POST.get('id')
            alert = ScheduleAlert.objects.get(id=aid)
            alert.area = request.POST['area']
            alert.service_id = request.POST['service_id']
            alert.title = request.POST['title']
            alert.message = request.POST['message']
            alert.priority = request.POST.get('priority', 'medium')
            alert.status = request.POST.get('status', 'active')
            alert.start_date = request.POST.get('start_date') or None
            alert.end_date = request.POST.get('end_date') or None
            alert.supervisor_name = request.POST.get('supervisor_name')
            alert.helpline_number = request.POST.get('helpline_number')
            alert.response_team_contact = request.POST.get('response_team_contact')
            alert.visibility_duration = request.POST.get('visibility_duration', 'permanent')
            alert.save()
            messages.success(request, "Alert updated successfully.")

        return redirect('service_admin')
        
    return redirect('service_admin')

@login_required
def payment_details_view(request):
    """User-facing page showing pricing tiers and allows searching payment status by tracking ID."""
    pricings = ComplaintPricingConfig.objects.filter(is_active=True)
    payment_record = None
    search_error = None
    tracking_id = None

    if request.method == "POST":
        tracking_id = request.POST.get('tracking_id', '').strip()
        try:
            complaint = Complaint.objects.get(complaint_id__iexact=tracking_id)
            payment_record = Payment.objects.filter(complaint=complaint).first()
            if not payment_record:
                if not complaint.payment_status:
                    search_error = "No payment record found. This complaint might still be awaiting payment."
                else:
                    search_error = "Complaint marked as 'Paid', but no transaction record found."
        except Complaint.DoesNotExist:
            search_error = "Invalid Tracking ID. Please check your system-generated ID."

    # Fetch active special pricing adjustment
    today = timezone.now().date()
    active_holiday = HolidayConfig.objects.filter(date=today, is_pricing_active=True).first()
    
    holiday_info = None
    if active_holiday:
        is_discount = active_holiday.price_multiplier < 1
        pct = abs(int((1 - active_holiday.price_multiplier) * 100)) if is_discount else abs(int((active_holiday.price_multiplier - 1) * 100))
        holiday_info = {
            'obj': active_holiday,
            'is_discount': is_discount,
            'percentage': pct
        }

    context = {
        'pricings': pricings,
        'payment_record': payment_record,
        'search_error': search_error,
        'tracking_id': tracking_id,
        'active_holiday': holiday_info
    }
    return render(request, 'accounts/payment_details.html', context)

@login_required
def payment_admin_view(request):
    """Staff-only view to manage pricing tiers and view all payments."""
    if not request.user.is_staff:
        messages.error(request, "Access Denied: Administrative permissions required.")
        return redirect('dashboard')
        
    pricings = ComplaintPricingConfig.objects.all()
    all_payments = Payment.objects.all().order_by('-date')
    holidays_queryset = HolidayConfig.objects.all().order_by('-date')
    
    # Calculate effect for each holiday for display
    holidays = []
    for h in holidays_queryset:
        is_discount = h.price_multiplier < 1
        pct = abs(int((1 - h.price_multiplier) * 100)) if is_discount else abs(int((h.price_multiplier - 1) * 100))
        h.is_discount = is_discount
        h.percentage = pct
        holidays.append(h)
    
    # Sort Pricing Tiers Numerically by Distance
    import re
    def get_distance_key(p):
        numbers = re.findall(r'\d+', p.distance_range)
        return int(numbers[0]) if numbers else 9999
        
    pricings_list = list(pricings)
    pricings_list.sort(key=get_distance_key)
    pricings = pricings_list
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add_pricing':
            ComplaintPricingConfig.objects.create(
                distance_range=request.POST['distance_range'],
                base_price=request.POST['base_price'],
                urgent_price=request.POST['urgent_price'],
                is_active='is_active' in request.POST
            )
            messages.success(request, "Pricing tier added.")
            
        elif action == 'edit_pricing':
            pid = request.POST.get('id')
            price = ComplaintPricingConfig.objects.get(id=pid)
            price.distance_range = request.POST['distance_range']
            price.base_price = request.POST['base_price']
            price.urgent_price = request.POST['urgent_price']
            price.is_active = 'is_active' in request.POST
            price.save()
            messages.success(request, "Pricing tier updated.")
            
        elif action == 'delete_pricing':
            ComplaintPricingConfig.objects.filter(id=request.POST.get('id')).delete()
            messages.warning(request, "Pricing tier removed.")

        elif action == 'edit_holiday_pricing':
            hid = request.POST.get('id')
            holiday = HolidayConfig.objects.get(id=hid)
            holiday.price_multiplier = request.POST.get('multiplier', 1.0)
            holiday.adjustment_description = request.POST.get('description', '')
            holiday.is_pricing_active = 'is_active' in request.POST
            holiday.save()
            messages.success(request, f"Pricing adjustments for {holiday.name} updated.")
            
        return redirect('payment_admin')

    context = {
        'pricings': pricings,
        'all_payments': all_payments,
        'holidays': holidays
    }
    return render(request, 'accounts/admin/payment_management.html', context)

@login_required
def admin_feedback_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    feedbacks = Feedback.objects.all().order_by('-rating', '-created_at')
    return render(request, 'accounts/admin/feedback_admin.html', {
        'feedbacks': feedbacks,
        'is_admin_view': True
    })

@login_required(login_url='login')
def delete_feedback_admin(request, id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    Feedback.objects.filter(id=id).delete()
    messages.warning(request, "Feedback entry deleted.")
    return redirect('admin_feedback')

@login_required(login_url='login')
def citizen_reviews_view(request):
    reviews = Feedback.objects.all().order_by('-rating', '-created_at')
    avg_rating = Feedback.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Calculate distribution
    distribution = {
        i: reviews.filter(rating=i).count() for i in range(1, 6)
    }
    
    context = {
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': reviews.count(),
        'distribution': distribution,
    }
    return render(request, 'accounts/citizen_reviews.html', context)

@login_required
def admin_notifications(request):
    """Admin view to manage and send announcements and personal notifications."""
    if not request.user.is_staff:
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
        
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'send_broadcast':
            Announcement.objects.create(
                title=request.POST['title'],
                message=request.POST['message'],
                alert_type=request.POST['alert_type'],
                is_active=True
            )
            messages.success(request, "System-wide announcement broadcasted!")
            
        elif action == 'send_personal':
            user_id = request.POST.get('user_id')
            try:
                target_user = User.objects.get(id=user_id)
                Notification.objects.create(
                    user=target_user,
                    title=request.POST['title'],
                    message=request.POST['message'],
                    alert_type=request.POST['alert_type']
                )
                messages.success(request, f"Personal notification sent to {target_user.username}.")
            except User.DoesNotExist:
                messages.error(request, "Target user not found.")
                
        elif action == 'delete_announcement':
            Announcement.objects.filter(id=request.POST.get('id')).delete()
            messages.warning(request, "Announcement removed.")
            
        elif action == 'delete_all_announcements':
            count = Announcement.objects.all().count()
            Announcement.objects.all().delete()
            messages.warning(request, f"Successfully cleared {count} active announcements.")
            
        return redirect('admin_notifications')

    context = {
        'announcements': Announcement.objects.all().order_by('-created_at'),
        'admin_notifications': AdminNotification.objects.all().order_by('-created_at')[:100],
        'users': User.objects.filter(is_staff=False).order_by('username'),
        'is_admin_view': True
    }
    return render(request, 'accounts/admin/notifications_admin.html', context)

@login_required
def admin_holiday_management(request):
    """
    Centralized admin module to manage holiday service plans, 
    special pricing, and service availability.
    """
    if not request.user.is_staff:
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
        
    holidays = HolidayConfig.objects.all().order_by('-date')
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add_holiday' or action == 'edit_holiday':
            hid = request.POST.get('id')
            defaults = {
                'name': request.POST['name'],
                'date': request.POST['date'],
                'is_active': 'is_active' in request.POST,
                'special_plan': request.POST.get('special_plan', ''),
                'price_multiplier': request.POST.get('price_multiplier', 1.0),
                'adjustment_description': request.POST.get('adjustment_description', ''),
                'is_pricing_active': 'is_pricing_active' in request.POST,
                'service_status': request.POST.get('service_status', 'Available Now'),
                'special_services': request.POST.get('special_services', ''),
                'coverage_tags': request.POST.get('coverage_tags', ''),
                'zones_covered': request.POST.get('zones_covered', ''),
                'holiday_type': request.POST.get('holiday_type', 'Public'),
            }
            
            if action == 'edit_holiday' and hid:
                HolidayConfig.objects.filter(id=hid).update(**defaults)
                messages.success(request, f"Updated holiday: {defaults['name']}")
            else:
                HolidayConfig.objects.create(**defaults)
                messages.success(request, f"Created new holiday service plan for {defaults['name']}")
                
        elif action == 'delete_holiday':
            HolidayConfig.objects.filter(id=request.POST.get('id')).delete()
            messages.warning(request, "Holiday service plan removed.")
            
        return redirect('admin_holiday')

    context = {
        'holidays': holidays,
        'status_choices': HolidayConfig.SERVICE_STATUS_CHOICES,
        'type_choices': HolidayConfig.HOLIDAY_TYPE_CHOICES,
        'is_admin_view': True
    }
    return render(request, 'accounts/admin/holiday_management.html', context)



@login_required(login_url='login')
def service_history_view(request):
    """View to display all private service bookings for the logged-in user."""
    bookings = ServiceBooking.objects.filter(user=request.user).order_by('-created_at')
    
    # Quick stats
    total = bookings.count()
    completed = bookings.filter(status='Completed').count()
    upcoming = bookings.filter(status__in=['Pending', 'Scheduled', 'In Progress']).count()
    
    context = {
        'bookings': bookings,
        'total': total,
        'completed': completed,
        'upcoming': upcoming
    }
    return render(request, 'accounts/service_history.html', context)

@login_required
def holiday_details_view(request, pk):
    """Dedicated view for city-wide holiday service plans."""
    holiday = get_object_or_404(HolidayConfig, pk=pk)
    
    # Calculate pricing stats if active
    pricing_info = None
    if holiday.is_pricing_active:
        is_discount = holiday.price_multiplier < 1
        pct = abs(int((1 - holiday.price_multiplier) * 100)) if is_discount else abs(int((holiday.price_multiplier - 1) * 100))
        pricing_info = {
            'is_discount': is_discount,
            'percentage': pct,
            'description': holiday.adjustment_description or "Special rates apply for today's services."
        }
    
    context = {
        'holiday': holiday,
        'pricing_info': pricing_info,
        'today': timezone.now().date()
    }
    return render(request, 'accounts/holiday_details.html', context)

@login_required
def get_admin_notifications(request):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)
    
    # Get unread operational alerts
    admin_notifs = AdminNotification.objects.filter(is_read=False).order_by('-created_at')[:50]
    # Get unread public system announcements for this user
    read_ann_ids = AnnouncementRead.objects.filter(user=request.user).values_list('announcement_id', flat=True)
    public_announcements = Announcement.objects.filter(is_active=True).exclude(id__in=read_ann_ids).order_by('-created_at')[:10]
    
    unread_count = admin_notifs.count()
    
    data = []
    # Add Admin Notifications
    for n in admin_notifs:
        data.append({
            'id': n.id,
            'source': 'admin',
            'type': n.type,
            'type_display': n.get_type_display(),
            'message': n.message,
            'link': n.link,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Add Public Announcements
    for a in public_announcements:
        data.append({
            'id': a.id,
            'source': 'public',
            'type': 'announcement',
            'type_display': 'System Announcement',
            'message': a.message,
            'link': reverse('notifications'),
            'is_read': False, # Returned announcements are unread
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Sort merged list by date
    data.sort(key=lambda x: x['created_at'], reverse=True)
    
    return JsonResponse({
        'status': 'success',
        'notifications': data[:40], # Show top 40 merged
        'unread_count': unread_count
    })

@login_required
def mark_admin_notifications_read(request):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)
    
    # 1. Mark admin notifications as read
    AdminNotification.objects.filter(is_read=False).update(is_read=True)
    
    # 2. Mark active announcements as read for this user
    active_announcements = Announcement.objects.filter(is_active=True)
    for ann in active_announcements:
        AnnouncementRead.objects.get_or_create(user=request.user, announcement=ann)
        
    return JsonResponse({'status': 'success'})

@login_required
def delete_admin_notification(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
    
    get_object_or_404(AdminNotification, id=pk).delete()
    messages.warning(request, "Operational log entry permanently removed.")
    return redirect('admin_notifications')

@login_required
def mark_single_admin_notification_read(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)
    
    notification = get_object_or_404(AdminNotification, id=pk)
    notification.is_read = True
    notification.save()
    return redirect('admin_notifications')

@login_required
def delete_all_admin_notifications(request):
    """Permanently removes all administrative operational log entries."""
    if not request.user.is_staff:
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
    
    count = AdminNotification.objects.all().count()
    AdminNotification.objects.all().delete()
    messages.warning(request, f"Successfully cleared {count} operational log entries.")
    return redirect('admin_notifications')


