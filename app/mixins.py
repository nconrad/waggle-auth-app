from rest_framework import serializers
from .models import ScienceField

class SchemaMixin:
    """Mixin to generate JSON Schema from DRF serializers"""

    def _get_field_type(self, field):
        """Map DRF field types to JSON Schema types"""
        if isinstance(field, (serializers.CharField, serializers.EmailField, serializers.URLField)):
            return "string"
        elif isinstance(field, serializers.IntegerField):
            return "integer"
        elif isinstance(field, serializers.BooleanField):
            return "boolean"
        elif isinstance(field, serializers.ListField):
            return "array"
        elif isinstance(field, serializers.DictField):
            return "object"
        return "string"

    def _get_field_schema(self, field):
        """Generate JSON Schema for a single field"""
        # Basic schema structure
        schema = {
            "type": self._get_field_type(field),
        }

        # Add title if available
        if field.label:
            schema["title"] = field.label
        elif field.field_name:
            schema["title"] = field.field_name.replace("_", " ").title()

        # Add description if available
        if field.help_text:
            schema["description"] = str(field.help_text)

        # Mark required fields
        if field.required:
            schema["required"] = True

        # Handle choice fields
        if isinstance(field, serializers.ChoiceField):
            # Get choices from the model field
            if hasattr(field.parent, 'Meta') and hasattr(field.parent.Meta, 'model'):
                model = field.parent.Meta.model
                model_field = model._meta.get_field(field.field_name)
                if hasattr(model_field, 'choices'):
                    choices = model_field.choices
                    if isinstance(choices, list) and len(choices) > 0 and isinstance(choices[0], (list, tuple)):
                        schema["enum"] = [choice[0] for choice in choices]
                        schema["enumNames"] = [choice[1] for choice in choices]
            # Fallback to field choices if model choices not found
            elif hasattr(field, 'choices') and field.choices:
                choices = field.choices
                if isinstance(choices, list) and len(choices) > 0 and isinstance(choices[0], (list, tuple)):
                    schema["enum"] = [choice[0] for choice in choices]
                    schema["enumNames"] = [choice[1] for choice in choices]

        # Handle list fields
        elif isinstance(field, serializers.ListField):
            if isinstance(field.child, serializers.ChoiceField):
                choices = field.child.choices
                if isinstance(choices, list) and len(choices) > 0 and isinstance(choices[0], (list, tuple)):
                    schema["items"] = {
                        "type": "string",
                        "enum": [choice[0] for choice in choices],
                        "enumNames": [choice[1] for choice in choices],
                    }
            else:
                schema["items"] = self._get_field_schema(field.child)

        # Handle nested serializers
        elif isinstance(field, serializers.ModelSerializer):
            schema["properties"] = {
                name: self._get_field_schema(f)
                for name, f in field.get_fields().items()
            }

        # Handle related fields
        elif isinstance(field, serializers.PrimaryKeyRelatedField):
            schema["type"] = "array"
            if field.field_name == 'science_fields':
                # For science fields, return names instead of IDs
                schema["items"] = {
                    "type": "string",
                    "enum": list(ScienceField.objects.values_list('name', flat=True))
                }
            else:
                # For other related fields, use IDs
                schema["items"] = {
                    "type": "integer",
                    "description": f"ID of the related {field.queryset.model.__name__}"
                }

        return schema

    def get_schema(self, serializer_class):
        """Generate JSON Schema from a serializer"""
        serializer = serializer_class()
        fields = serializer.get_fields()

        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }

        # Add fields to schema
        for field_name, field in fields.items():
            schema["properties"][field_name] = self._get_field_schema(field)
            if field.required:
                schema["required"].append(field_name)

        return schema