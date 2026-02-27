from django.contrib import admin

from island.models import Island
from .models import Country


class IslandInline(admin.TabularInline):
    model = Island
    extra = 1
    min_num = 1
    validate_min = True

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name')
    inlines = (IslandInline,)
