from django.contrib import admin
from .models import Restaurant, ServiceTime, RestaurantReview
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = [
    	'__str__', 'saturday', 'sunday', 
    	'monday', 'tuesday', 'wednesday', 'thursday', 
    	'friday'
    ]
    list_editable = [
    	'saturday', 'sunday', 'monday', 
        'tuesday', 'wednesday', 'thursday', 
    	'friday'
    ]
    class Meta:
        model = Restaurant

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'is_active', 'is_orderable', 'created_at')
    list_filter = ('is_active', 'is_orderable', 'city')
    search_fields = ('title', 'address')
    prepopulated_fields = {"slug": ("title",)}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in ['phone', 'email', 'address', 'environment', 'map_embed_url', 'extra_info']:
            form.base_fields[field].widget.attrs['readonly'] = False
        return form



admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(ServiceTime, ServiceTimeAdmin)
admin.site.register(RestaurantReview)