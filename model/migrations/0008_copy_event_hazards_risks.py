from django.db import migrations


def copy_event_hazards_risks(apps, schema_editor):
    """Move each event's hazards/risks onto the event's model run (if it has one)."""
    Event = apps.get_model("event", "Event")
    for event in Event.objects.exclude(model_run=None).prefetch_related("hazards", "risks"):
        event.model_run.hazards.add(*event.hazards.all())
        event.model_run.risks.add(*event.risks.all())


class Migration(migrations.Migration):

    dependencies = [
        ("model", "0007_modelrun_hazards_risks"),
        ("event", "0004_event_event_datetime_event_title"),
    ]

    operations = [
        migrations.RunPython(copy_event_hazards_risks, migrations.RunPython.noop),
    ]
