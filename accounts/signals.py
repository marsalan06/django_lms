from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def send_user_credentials(sender, instance, created, **kwargs):
    if created:
        print("-------user name-----: ", instance.username)
        print("-------password------: ", instance.generated_password)
        # Send email with the generated credentials
        send_mail(
            "Your Django LMS account credentials",
            f"Your username: {instance.username}\nYour password: {instance.generated_password}",
            settings.EMAIL_FROM_ADDRESS,
            [instance.email],
            fail_silently=False,
        )
