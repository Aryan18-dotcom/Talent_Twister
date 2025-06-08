from datetime import date

def assign_priority_color(tasks):
    """Assigns a color based on task priority for Task and TaskProgress models."""
    for task_obj in tasks:
        task = task_obj.task if hasattr(task_obj, 'task') else task_obj  # Get Task from TaskProgress or Task
        
        task.color = {
            'High': 'red',
            'Medium': 'yellow'
        }.get(task.task_priority, 'blue')  # Default color is blue
        
        # If it's a TaskProgress object, ensure it gets the same color
        if hasattr(task_obj, 'task'):
            task_obj.color = task.color  

    return tasks


def calculate_task_progress(task):
    """Calculate task progress percentage, days remaining, and overdue status."""
    todayDate = date.today()

    if not task.created_at:
        task.progress_date = 0
        task.days_remaining = None
        task.is_due_today = False
        task.is_overdue = False
        return task

    if task.due_date:
        dueDate = task.due_date
        created_at_date = task.created_at.date()

        total_days = (dueDate - created_at_date).days
        elapsed_days = (todayDate - created_at_date).days

        if dueDate == todayDate:
            task.progress_date = 99
            task.days_remaining = 0
            task.is_due_today = True
            task.is_overdue = False
        elif todayDate > dueDate:  # Task is overdue
            task.progress_date = 100
            task.days_remaining = (todayDate - dueDate).days  # Ensure positive value
            task.is_due_today = False
            task.is_overdue = True
        else:
            progress = min(100, max(0, (elapsed_days / total_days) * 100)) if total_days > 0 else 0
            task.progress_date = progress
            task.days_remaining = (dueDate - todayDate).days
            task.is_due_today = False
            task.is_overdue = False
    else:
        task.progress_date = 0
        task.days_remaining = None
        task.is_due_today = False
        task.is_overdue = False

    return task




