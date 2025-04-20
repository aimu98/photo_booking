from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date

class Reservation(models.Model):
    PLAN_CHOICES = [
        ('basic', 'ベーシックプラン'),
        ('753', '七五三プラン'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("名前", max_length=100)
    children_name = models.CharField("お子様のお名前", max_length=100)
    email = models.EmailField("メールアドレス")
    phone = models.CharField("電話番号", max_length=15)
    date = models.DateField("予約日")
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    message = models.TextField("ご不明点やご要望などお気軽にお書きください" , blank=True)
    
    def __str__(self):
        return f"{self.user} - {self.get_plan_display()}"
    
    @property
    def can_cancel(self):
        return (self.date - date.today()).days >= 3
    
    @property
    def can_edit(self):
        return (self.date - date.today()).days >= 1 
    
    @staticmethod
    def get_reserved_times(date):
        reservations = Reservation.objects.filter(date=date)
        reserved_times = [(r.start_time, r.end_time) for r in reservations]
        return reserved_times
    
    

    class Meta:
        unique_together = ('date', 'start_time')  # 二重予約防止

    def __str__(self):
        return f"{self.name} - {self.date} {self.start_time}"
    
    def is_cancellable(self):
        return (self.date - date.today()) >= timedelta(days=3)
    

class AvailableSlot(models.Model):
    date = models.DateField("日付")  
    start_time = models.TimeField("開始時間")  
    end_time = models.TimeField("終了時間") 

    class Meta:
        unique_together = ('date', 'start_time')

    def __str__(self):
        return f"{self.date} {self.start_time} - {self.end_time}"

