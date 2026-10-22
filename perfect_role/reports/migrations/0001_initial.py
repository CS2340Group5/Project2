import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('posts', '0010_alter_jobpost_skills'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.CharField(choices=[('USER', 'User'), ('POST', 'Job Posting')], max_length=10)),
                ('target_summary', models.CharField(blank=True, max_length=255)),
                ('reason', models.CharField(choices=[('INAPPROPRIATE', 'Inappropriate content'), ('MISLEADING', 'Misleading or fraudulent'), ('ABUSIVE', 'Abusive or harassing behavior'), ('SPAM', 'Spam'), ('OTHER', 'Other')], default='INAPPROPRIATE', max_length=15)),
                ('details', models.TextField(blank=True, max_length=1000)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('INVESTIGATING', 'Under Investigation'), ('RESOLVED', 'Resolved'), ('DISMISSED', 'Dismissed')], default='PENDING', max_length=15)),
                ('action_taken', models.CharField(choices=[('NONE', 'No action'), ('USER_WARNED', 'User warned'), ('POST_REMOVED', 'Job posting removed'), ('USER_DEACTIVATED', 'User deactivated')], default='NONE', max_length=20)),
                ('admin_notes', models.TextField(blank=True, max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('reported_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports', to='posts.jobpost')),
                ('reported_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_received', to=settings.AUTH_USER_MODEL)),
                ('reporter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_made', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_reviewed', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
