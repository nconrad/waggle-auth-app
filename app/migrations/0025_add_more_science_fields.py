from django.db import migrations

def add_more_science_fields(apps, schema_editor):
    ScienceField = apps.get_model('app', 'ScienceField')
    additional_fields = [
        'Agricultural Science',
        'Astronomy',
        'Atmospheric Science',
        'Biochemistry',
        'Biotechnology',
        'Chemistry',
        'Climate Science',
        'Cognitive Science',
        'Data Science',
        'Earth Science',
        'Ecology',
        'Environmental Science',
        'Genetics',
        'Geology',
        'Geophysics',
        'Information Science',
        'Materials Science',
        'Mathematics',
        'Medicine',
        'Microbiology',
        'Molecular Biology',
        'Neuroscience',
        'Oceanography',
        'Pharmacology',
        'Psychology',
        'Public Health',
        'Robotics',
        'Social Science',
        'Space Science',
        'Statistics',
        'Systems Biology',
        'Urban Science',
        'Veterinary Science',
        'Wildlife Biology',
    ]
    for field_name in additional_fields:
        ScienceField.objects.get_or_create(name=field_name)

def reverse_add_more_science_fields(apps, schema_editor):
    ScienceField = apps.get_model('app', 'ScienceField')
    ScienceField.objects.filter(name__in=[
        'Agricultural Science',
        'Astronomy',
        'Atmospheric Science',
        'Biochemistry',
        'Biotechnology',
        'Chemistry',
        'Climate Science',
        'Cognitive Science',
        'Data Science',
        'Earth Science',
        'Ecology',
        'Environmental Science',
        'Genetics',
        'Geology',
        'Geophysics',
        'Information Science',
        'Materials Science',
        'Mathematics',
        'Medicine',
        'Microbiology',
        'Molecular Biology',
        'Neuroscience',
        'Oceanography',
        'Pharmacology',
        'Psychology',
        'Public Health',
        'Robotics',
        'Social Science',
        'Space Science',
        'Statistics',
        'Systems Biology',
        'Urban Science',
        'Veterinary Science',
        'Wildlife Biology',
    ]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0024_add_interest_in_hpc_to_allocation_project'),
    ]

    operations = [
        migrations.RunPython(add_more_science_fields, reverse_add_more_science_fields),
    ]