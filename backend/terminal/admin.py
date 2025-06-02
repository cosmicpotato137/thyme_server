from django.contrib import admin
import terminal.models as models

# Register your models here.


@admin.register(models.CommandHistory)
class CommandHistoryAdmin(admin.ModelAdmin):
    list_display = ("command", "timestamp")
    search_fields = ("command",)
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
