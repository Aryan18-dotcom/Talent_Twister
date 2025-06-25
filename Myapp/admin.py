from django.contrib import admin
from django.utils.html import format_html
from .models import Company, Employee, TeamLead, JobSeeker, Task, TaskProgress, WorkLeave, Skill, Education, Experience, Team, HR, Co_Curricular
from django import forms


# admin.site.register([Chat, Message])

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1

class Co_Curricularline(admin.TabularInline):
    model = Co_Curricular
    extra = 1


# Common mixin for image display
class ImageDisplayMixin:
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.image.url
            )
        return format_html(
            '<div style="width:50px; height:50px; background:#eee; border-radius:50%; display:flex; align-items:center; justify-content:center;">'
            '<span style="color:#999;">No Image</span>'
            '</div>'
        )
    image_thumbnail.short_description = 'Profile'
    image_thumbnail.allow_tags = True


@admin.register(HR)
class HRAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ('id', 'image_thumbnail', 'username', 'full_name', 'company', 'is_active', 'status', 'edit_link')
    list_filter = ('gender', 'status', 'is_active')
    search_fields = ('username', 'full_name', 'email', 'hr_id')
    list_editable = ('is_active', 'status')
    list_display_links = ('username',)
    list_per_page = 25
    # inlines = [Co_Curricular]

    def edit_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            f'{obj.id}/change/'
        )
    edit_link.short_description = 'Edit'




@admin.register(TeamLead)
class TeamLeadAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ('id', 'image_thumbnail', 'username', 'company_name', 'full_name', 'email', 'is_active', 'role', 'edit_link')
    list_filter = ('is_active', 'role', 'created_companies')
    search_fields = ('username', 'full_name', 'email', 'created_companies__name')
    list_editable = ('is_active', 'role')
    list_display_links = None
    list_per_page = 20
    inlines = [Co_Curricularline,]


    def company_name(self, obj):
        # Get the first company created by this HR
        company = obj.created_companies.first()
        return company.name if company else "No Company"
    company_name.short_description = 'Company'

    def edit_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            f'{obj.id}/change/'
        )
    edit_link.short_description = ''



class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If the instance exists (i.e. editing a team)
        if self.instance and self.instance.pk:
            self.fields['members'].queryset = Employee.objects.filter(company=self.instance.company)
        else:
            self.fields['members'].queryset = Employee.objects.none()

@admin.register(Team)
class TeamsAdmin(admin.ModelAdmin):
    form = TeamForm
    list_display = ('id', 'name', 'created_by', 'created_at', 'total_members', 'is_active', 'edit_link')
    list_filter = ('name', 'is_active', 'created_by')
    search_fields = ('name', 'created_by__username')  # or 'created_by__full_name' if it exists
    list_editable = ('is_active',)
    list_display_links = None
    list_per_page = 20

    def edit_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            f'{obj.id}/change/'
        )
    edit_link.short_description = 'Edit'



@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ('id', 'image_thumbnail', 'username', 'full_name', 'company', 'is_active', 'role', 'edit_link')
    search_fields = ('username', 'full_name', 'email', 'company__name')
    list_filter = ('company', 'is_active', 'role')
    list_editable = ('is_active', 'role')
    list_per_page = 20
    inlines = [SkillInline, EducationInline, ExperienceInline]

    def edit_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            f'{obj.id}/change/'
        )
    edit_link.short_description = ''


@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ('id', 'image_thumbnail', 'username', 'full_name', 'email', 'edit_link')
    search_fields = ('username', 'full_name', 'email')
    list_per_page = 20

    def edit_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            f'{obj.id}/change/'
        )
    edit_link.short_description = ''

# Other Admin classes remain the same as previous implementation
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'domain', 'edit_actions')
    search_fields = ('name', 'domain')
    list_per_page = 20

    def edit_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}">Delete</a>',
            f'{obj.id}/change/',
            f'{obj.id}/delete/'
        )
    edit_actions.short_description = 'Actions'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'assigned_by', 'assigned_to', 'status', 'task_priority', 'due_date', 'created_at', 'edit_link')
    search_fields = ('title', 'assigned_by__username', 'assigned_to__username')
    list_filter = ('status', 'task_priority', 'assigned_by', 'assigned_to')
    list_editable = ('status', 'task_priority')
    list_per_page = 20
    date_hierarchy = 'created_at'

    def edit_link(self, obj):
        return format_html('<a href="{}">Edit</a>', f'{obj.id}/change/')
    edit_link.short_description = ''

@admin.register(TaskProgress)
class TaskProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_title', 'employee', 'status', 'completion_type', 'action_date_short', 'completion_date_short', 'days_difference', 'edit_link')
    search_fields = ('task__title', 'employee__username')
    list_filter = ('status', 'completion_type', 'employee')
    list_editable = ('status', 'completion_type')
    list_per_page = 20
    date_hierarchy = 'completion_date'

    def task_title(self, obj):
        return obj.task.title
    task_title.short_description = 'Task'

    def action_date_short(self, obj):
        return obj.action_date.strftime("%Y-%m-%d %H:%M") if obj.action_date else "-"
    action_date_short.short_description = 'Started'

    def completion_date_short(self, obj):
        return obj.completion_date.strftime("%Y-%m-%d %H:%M") if obj.completion_date else "-"
    completion_date_short.short_description = 'Completed'

    def edit_link(self, obj):
        return format_html('<a href="{}">Edit</a>', f'{obj.id}/change/')
    edit_link.short_description = ''


@admin.register(WorkLeave)
class WorkLeaveAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'leave_type', 'start_date', 'end_date', 'status', 'applied_at', 'edit_link')
    search_fields = ('user__username', 'leave_type', 'status')
    list_filter = ('status', 'leave_type', 'start_date', 'end_date')
    list_per_page = 20
    date_hierarchy = 'start_date'

    def edit_link(self, obj):
        return format_html('<a href="{}">Edit</a>', f'{obj.id}/change/')
    edit_link.short_description = ''


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'employee')
    search_fields = ('name', 'employee__username')
    list_filter = ('employee',)

@admin.register(Co_Curricular)
class CoCurricularAdmin(admin.ModelAdmin):
    list_display = ('name', 'Hr', 'proficiency')
    search_fields = ('name', 'Hr__username')
    list_filter = ('proficiency',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('id', 'degree', 'institution', 'employee', 'start_year', 'end_year')
    search_fields = ('degree', 'institution', 'employee__username')
    list_filter = ('employee',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_title', 'company_name', 'employee', 'start_date', 'end_date')
    search_fields = ('job_title', 'company_name', 'employee__username')
    list_filter = ('employee',)

