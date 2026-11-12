from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    name = models.CharField(
        max_length=200, help_text='e.g., 4-Cock Hackfight, Special Derby'
    )
    date = models.DateField()
    is_active = models.BooleanField(
        default=True,
        help_text='Mark TRUE for the current ongoing event (only 1 active at a time)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure only ONE event is active at a time
        if self.is_active:
            Event.objects.filter(is_active=True).exclude(id=self.id).update(
                is_active=False
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.date})'


class Teller(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('REQUEST', 'Request Cash (Float)'),
        ('PARTIAL', 'Partial Collection'),
    )

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='transactions'
    )
    it_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='collections'
    )
    teller = models.ForeignKey(
        Teller, on_delete=models.CASCADE, related_name='transactions'
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Media captures (Both strictly required)
    signature = models.ImageField(upload_to='signatures/%Y/%m/%d/')
    photo = models.ImageField(upload_to='teller_photos/%Y/%m/%d/')

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[{self.event.name}] {self.teller.name} ({self.transaction_type}): ₱{self.amount}'