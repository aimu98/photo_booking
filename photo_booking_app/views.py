from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .forms import ReservationForm, AvailableSlotForm,ReservationEditForm
from .models import Reservation , AvailableSlot
from datetime import datetime, time, timedelta , date
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model

def reservation_form(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reservation_done')
    else:
        form = ReservationForm()
    return render(request, 'photo_booking_app/reservation_form.html', {'form': form})

def reservation_done(request):
    return render(request, 'photo_booking_app/reservation_done.html')

def get_available_dates(request):
    available_slots = AvailableSlot.objects.values_list('date', flat=True).distinct()
    dates = [slot.strftime('%Y-%m-%d') for slot in available_slots]
    return JsonResponse({'available_dates': dates})

def get_available_times(request):
    date_str = request.GET.get('date')  # 'YYYY-MM-DD'
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'available_times': []})

    available_slots = AvailableSlot.objects.filter(date=date_obj)
    reserved_slots = Reservation.objects.filter(date=date_obj)

    reserved_times = [(r.start_time, r.end_time) for r in reserved_slots]

    available_times = []
    for slot in available_slots:
        if (slot.start_time, slot.end_time) not in reserved_times:
            formatted = f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
            available_times.append(formatted)

    return JsonResponse({'available_times': available_times})

def available_slots_view(request):
    available_slots = AvailableSlot.objects.all()
    return render(request, 'photo_booking_app/available_slots.html', {'available_slots': available_slots})


def add_available_slot(request):
    if request.method == 'POST':
        form = AvailableSlotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_available_slots')  # 予約可能日時の一覧ページにリダイレクト
    else:
        form = AvailableSlotForm()

    return render(request, 'photo_booking_app/add_available_slot.html', {'form': form})

def add_event_to_google_calendar(reservation):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': f'📷 予約: {reservation.name}',
        'description': reservation.message,
        'start': {
            'dateTime': datetime.combine(reservation.slot.date, reservation.slot.start_time).isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': datetime.combine(reservation.slot.date, reservation.slot.end_time).isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
    }

    service.events().insert(calendarId='ay.1031.ld@group.calendar.google.com', body=event).execute()
    
@login_required
def reservation_history(request):
    today = date.today()
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'photo_booking_app/reservation_history.html', {
        'reservations': reservations,
        'today': today,
    })

@login_required
def reservation_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user  
            reservation.save()

             # ✅ メール送信（お客様宛）
            send_mail(
                subject='【予約完了】撮影予約が確定しました',
                message=f'{request.user.username}様\n\n以下の内容で撮影予約が確定しました。\n\n日付: {reservation.date}\n時間: {reservation.start_time}〜{reservation.end_time}\nプラン: {reservation.plan}\n\n当日お待ちしております！',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            # ✅ メール送信（管理者宛）
            send_mail(
                subject='【通知】新しい撮影予約が入りました',
                message=f'{request.user.username}様より撮影予約が入りました。\n\n日付: {reservation.date}\n時間: {reservation.start_time}〜{reservation.end_time}\nプラン: {reservation.plan}\n\n管理画面で確認してください。',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],  # または [admin@example.com]
                fail_silently=False,
            )

            messages.success(request, '予約が完了しました。確認メールを送信しました。')
            return redirect('reservation_done')
    else:
        form = ReservationForm()
    return render(request, 'photo_booking_app/reservation_form.html', {'form': form})

  
@require_POST  
@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if (reservation.date - date.today()).days >= 3:
        reservation.delete()
        messages.success(request, "予約をキャンセルしました。")
    else:
        messages.error(request, "3日以内の予約はキャンセルできません。")

    return redirect('reservation_history')


@login_required
def mypage(request):
    return render(request, 'accounts/mypage.html')
    
def test_mail(request):
    send_mail(
        'テストメール件名',
        'これはDjangoからのテストメールです。',
        'ay.1031.ld@gmail.com',  # 送信者
        ['furutono.a.b'],     # 受信者
        fail_silently=False,
    )
    return HttpResponse("テストメールを送信しました！")

@login_required
def reservation_history(request):
    today = timezone.localdate()
    reservations = Reservation.objects.filter(user=request.user)

    return render(request, 'accounts/reservation_history.html', {
        'reservations': reservations,
        'today': today
    })


def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, 'photo_booking_app/reservation_detail.html', {'reservation': reservation})

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if (reservation.date - date.today()).days < 3:
        messages.error(request, "3日以内の予約は編集できません。")
        return redirect('reservation_history')

    if request.method == 'POST':
        form = ReservationEditForm(request.POST, instance=reservation)
        if form.is_valid():
            updated_reservation = form.save()
            messages.success(request, "予約内容を更新しました。")
            
            send_mail(
                subject='【予約変更通知】予約が編集されました',
                message=(
                    f"以下の予約がユーザー {request.user.username} によって変更されました：\n\n"
                    f"予約日: {updated_reservation.date}\n"
                    f"時間: {updated_reservation.start_time} ～ {updated_reservation.end_time}\n"
                    f"プラン: {updated_reservation.plan}\n"
                    f"名前: {updated_reservation.name}\n"
                    f"お子様の名前: {updated_reservation.children_name}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL, request.user.email],
                fail_silently=False,
            )
            return redirect('reservation_history')
    else:
        form = ReservationEditForm(instance=reservation)

    return render(request, 'photo_booking_app/edit_reservation.html', {'form': form, 'reservation': reservation})

@staff_member_required
def admin_reservation_dashboard(request):
    reservations = Reservation.objects.all()
    return render(request, 'photo_booking_app/admin_dashboard.html', {'reservations': reservations})

def admin_reservation_list(request, user_id=None):
     
    users = User.objects.all()
     
    if user_id:
        reservations = Reservation.objects.filter(user__id=user_id).order_by('-date', '-start_time')
    else:
        reservations = Reservation.objects.all().order_by('-date', '-start_time')

    return render(request, 'photo_booking_app/admin_reservation_list.html', {'reservations': reservations})

def logout_done(request):
    return render(request, 'photo_booking_app/logout_done.html')

def home(request):
    return render(request, 'home.html', {'hide_header': True})

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass 
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(user.pk.encode())
            domain = get_current_site(request).domain
            link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = f'http://{domain}{link}'
            
            
            subject = "パスワードリセットリンク"
            message = render_to_string('password_reset_email.html', {
                'reset_url': reset_url,
            })
            send_mail(subject, message, 'no-reply@example.com', [email])
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_request.html', {'form': form})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
   
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password = request.POST.get('password')
                user.set_password(password)
                user.save()
                return redirect('password_reset_complete')
            return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
    except Exception:
        pass
    return redirect('password_reset')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')