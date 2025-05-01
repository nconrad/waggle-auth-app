from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from node_auth.contrib.auth.models import AbstractNode
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from node_auth.models import Token
import re
import uuid

ssh_public_key_re = re.compile(r"^ssh-(\S+) (\S+)")


def validate_ssh_public_key_list(value: str):
    lines = value.splitlines()
    if len(lines) > 5:
        raise ValidationError(
            f"You may only have up to five keys.", params={"value": value}
        )
    for line in lines:
        if not ssh_public_key_re.match(line):
            raise ValidationError(
                f"Enter a valid list of newline delimited SSH public keys.",
                params={"value": value},
            )


class User(AbstractUser):
    # use uuid as primary key to more directly support systems like globus
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # use name instead of assuming cultural convention first and last name.
    name = models.CharField(blank=True, max_length=255)
    first_name = None
    last_name = None
    # profile info
    organization = models.CharField(blank=True, max_length=255)
    department = models.CharField(blank=True, max_length=255)
    bio = models.TextField(blank=True, max_length=2000)
    ssh_public_keys = models.TextField(
        "SSH public keys", blank=True, validators=[validate_ssh_public_key_list]
    )
    is_approved = models.BooleanField(
        "Approval status",
        default=False,
        help_text="Designates whether the user is approved to perform basic tasks such as submitting apps to ECR.",
    )

    def get_absolute_url(self):
        return reverse("app:user-detail", kwargs={"username": self.username})


class Node(AbstractNode):
    mac = models.CharField("MAC", max_length=16, unique=True, null=True, blank=True)
    files_public = models.BooleanField(default=False)
    commissioning_date = models.DateTimeField(null=True, blank=True)


@receiver(post_save, sender=Node)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(node=instance)


# NOTE This Project is more like a permissions group a node / user can be a part of
# as opposed to an organizational project (ex. Sage, DAWN, VTO) who owns a node.
#
# Eventually, we should clarify the name or how this is done.
class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    include_in_api = models.BooleanField(default=True)  # should the project be included in the api
    users = models.ManyToManyField(User, through="UserMembership")
    nodes = models.ManyToManyField(Node, through="NodeMembership")

    def __str__(self):
        return self.name

    def number_of_users(self):
        return self.users.count()

    def number_of_nodes(self):
        return self.nodes.count()



class UserMembership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_schedule = models.BooleanField(
        "Schedule?", default=False, help_text="Designates whether user can schedule."
    )
    can_develop = models.BooleanField(
        "Develop?",
        default=False,
        help_text="Designates whether user has developer access.",
    )
    can_access_files = models.BooleanField(
        "Files?", default=False, help_text="Designates whether user has file access."
    )
    allow_view = models.BooleanField(
        "View?",
        default=False,
        help_text="Designates whether user has view access to project.",
    )

    def __str__(self):
        return f"{self.user} | {self.project}"

    # TODO(sean) UniqueConstraint seem to cause a bug as of Django 4.1, will investigate later.
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint("user", "project", name="app_profilemembership_uniq")
    #     ]


class NodeMembership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    can_schedule = models.BooleanField(
        "Schedule?",
        default=False,
        help_text="Designates whether node allows scheduling.",
    )
    can_develop = models.BooleanField(
        "Develop?",
        default=False,
        help_text="Designates whether node allows developer access.",
    )

    def __str__(self):
        return f"{self.node} | {self.project}"

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint("node", "project", name="app_nodemembership_uniq")
    #     ]



class FundingSource(models.Model):
    source = models.CharField(max_length=255)
    grant_number = models.CharField(max_length=255)


class ScienceField(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class AllocationRequest(models.Model):
    PROJECT_REQUEST_TYPE_CHOICES = [
        ('new', 'Request new project'),
        ('renew', 'Renew existing project'),
        ('add', 'Request add to existing project'),
    ]

    project_request_type = models.CharField(
        max_length=10,
        choices=PROJECT_REQUEST_TYPE_CHOICES,
        default='new',
        verbose_name="Project Request Type"
    )

    existing_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)

    # Fields moved from AllocationProject
    pi_name = models.CharField(max_length=255, null=True, blank=True)
    pi_email = models.EmailField(null=True, blank=True)
    pi_institution = models.CharField(max_length=255, null=True, blank=True)
    project_title = models.CharField(max_length=255, null=True, blank=True)
    project_website = models.URLField(blank=True, null=True)
    project_short_name = models.CharField(max_length=100, null=True, blank=True)
    science_fields = models.ManyToManyField(ScienceField)

    PROPOSAL_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    related_to_proposal = models.CharField(max_length=10, choices=PROPOSAL_CHOICES, null=True, blank=True)
    justification = models.TextField(blank=True, null=True)

    funding_sources = models.ManyToManyField(FundingSource)

    access_running_apps = models.BooleanField(default=False)
    access_shell = models.BooleanField(default=False)
    access_download = models.BooleanField(default=False)

    interest_in_hpc = models.BooleanField(
        verbose_name="Are you interested in using HPC resources with Sage data?",
        default=False
    )

    comments = models.TextField(
        verbose_name="Additional Comments",
        blank=True,
        null=True,
        help_text="Any additional comments or information you'd like to provide"
    )

    is_approved = models.BooleanField(
        "Approval status",
        default=False,
        help_text="Has the project been approved?"
    )




