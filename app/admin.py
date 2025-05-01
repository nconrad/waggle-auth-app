from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django import forms
from .models import User, Node, Project, UserMembership, NodeMembership, \
    AllocationRequest, FundingSource, ScienceField


class UserMembershipInline(admin.TabularInline):
    ordering = ("user__username",)
    model = UserMembership
    extra = 0
    autocomplete_fields = ["user", "project"]


class NodeMembershipInline(admin.TabularInline):
    ordering = ("node__vsn",)
    model = NodeMembership
    extra = 0
    autocomplete_fields = ["node", "project"]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "name",
                    "email",
                    "organization",
                    "department",
                    "bio",
                    "ssh_public_keys",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_approved",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "name", "email", "is_superuser", "is_approved")
    list_filter = ("is_superuser", "is_approved")
    search_fields = ("username", "name")
    inlines = (UserMembershipInline,)


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("vsn", "mac", "commissioning_date", "files_public")
    list_filter = ("files_public",)
    search_fields = ("vsn", "mac")
    ordering = ("vsn",)
    inlines = (NodeMembershipInline,)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "number_of_users", "number_of_nodes")
    list_filter = ("include_in_api",)  # Enable filtering by API inclusion
    search_fields = ("name",)
    inlines = (UserMembershipInline, NodeMembershipInline)


@admin.register(ScienceField)
class ScienceFieldAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(FundingSource)
class FundingSourceAdmin(admin.ModelAdmin):
    list_display = ('source', 'grant_number')
    search_fields = ('source', 'grant_number')


@admin.register(AllocationRequest)
class AllocationRequestAdmin(admin.ModelAdmin):
    list_display = ('username', 'project_request_type', 'existing_project', 'is_approved')
    search_fields = ('username',)
    list_filter = ('is_approved', 'project_request_type')
    filter_horizontal = ('science_fields', 'funding_sources')

    fieldsets = (
        (None, {
            'fields': ('username', 'is_approved')
        }),
        ('Project Selection', {
            'fields': ('project_request_type', 'existing_project'),
            'description': 'Select whether to request a new project, renew an existing one, or be added to an existing project.'
        }),
        ('Project Details', {
            'fields': (
                'pi_name',
                'pi_email',
                'pi_institution',
                'project_title',
                'project_website',
                'project_short_name',
                'science_fields',
                'related_to_proposal',
                'justification',
                'funding_sources',
            ),
            'classes': ('project-details',),
        }),
        ('Access Permissions', {
            'fields': (
                'access_running_apps',
                'access_shell',
                'access_download',
            ),
            'classes': ('access-permissions',),
        }),
        ('High Performance Computing', {
            'fields': ('interest_in_hpc',),
            'classes': ('hpc-interest',),
        }),
        ('Additional Information', {
            'fields': ('comments',),
            'classes': ('additional-info',),
        }),
    )

    class Media:
        js = ('admin/js/allocation_request.js',)
