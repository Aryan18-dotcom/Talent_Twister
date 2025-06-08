from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, TaskProgress

# Ensure TaskProgress status syncs with Task status
@receiver(post_save, sender=Task)
def sync_task_progress_status(sender, instance, **kwargs):
    # When the Task status changes, update related TaskProgress entries
    if instance.status:
        TaskProgress.objects.filter(task=instance).update(status=instance.status)
