from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Project, AllocationRequest, FundingSource, ScienceField

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "url",
            "username",
            "email",
            "name",
            "is_staff",
            "is_superuser",
            "is_approved",
            "ssh_public_keys",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "username", "view_name": "app:user-detail"},
            "users": {"lookup_field": "username"},
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        lookup_field = "username"
        fields = ["username", "organization", "department", "bio", "ssh_public_keys"]
        read_only_fields = ["username"]



class ProjectSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )
    nodes = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="vsn"
    )

    class Meta:
        model = Project
        fields = ["name", "users", "nodes", "number_of_users", "number_of_nodes"]


class FundingSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingSource
        fields = ['source', 'grant_number']

class AllocationRequestSerializer(serializers.ModelSerializer):
    science_fields = serializers.PrimaryKeyRelatedField(
        queryset=ScienceField.objects.all(),
        many=True,
        required=False
    )
    funding_sources = serializers.PrimaryKeyRelatedField(
        queryset=FundingSource.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = AllocationRequest
        lookup_field = "username"
        fields = [
            "username", "project_request_type", "existing_project",
            "pi_name", "pi_email", "pi_institution",
            "project_title", "project_website", "project_short_name",
            "science_fields", "related_to_proposal", "justification",
            "funding_sources", "access_running_apps", "access_shell",
            "access_download", "interest_in_hpc", "comments"
        ]
        read_only_fields = ["is_approved"]

    def validate(self, data):
        if data.get('project_request_type') == 'new':
            required_fields = [
                'pi_name', 'pi_email', 'pi_institution',
                'project_title', 'project_short_name',
                'science_fields', 'related_to_proposal',
                'funding_sources'
            ]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f"This field is required when requesting a new project."
                    })
        return data

    def create(self, validated_data):
        funding_sources_data = validated_data.pop('funding_sources', [])
        science_fields_data = validated_data.pop('science_fields', [])

        allocation_request = AllocationRequest.objects.create(**validated_data)

        # Add funding sources
        for funding_source in funding_sources_data:
            allocation_request.funding_sources.add(funding_source)

        # Add science fields
        for science_field in science_fields_data:
            allocation_request.science_fields.add(science_field)

        return allocation_request

class AllocationRequestFormDataSerializer(serializers.Serializer):
    science_fields = serializers.ListField(child=serializers.CharField())
    project_request_types = serializers.ListField(child=serializers.CharField())
    funding_sources = serializers.ListField(child=serializers.CharField())
    access_permissions = serializers.ListField(child=serializers.CharField())
    proposal_choices = serializers.ListField(child=serializers.CharField())
    projects = ProjectSerializer(many=True)





