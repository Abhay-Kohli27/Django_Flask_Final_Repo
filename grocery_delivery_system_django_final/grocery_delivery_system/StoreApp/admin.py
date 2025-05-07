from django.contrib import admin
from .models import Store
import requests

class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'owner_name', 'is_approved', 'store_category', 'business_email')
    list_filter = ('is_approved', 'store_category')
    search_fields = ('store_name', 'owner_name', 'business_email')
    actions = ['approve_selected_stores']
    list_editable = ['is_approved']

    def approve_selected_stores(self, request, queryset):
        approved_count = 0

        print("hello") 
        for store in queryset:
            if not store.is_approved:
                store.is_approved = True
                store.save()
                self.call_flask_api(store.store_id, request)
                approved_count += 1

        self.message_user(request, f"{approved_count} store(s) successfully approved and synced with Flask.")

    approve_selected_stores.short_description = "Approve selected store applications"

    def save_model(self, request, obj, form, change):
        was_previously_approved = Store.objects.get(pk=obj.pk).is_approved if obj.pk else False
        super().save_model(request, obj, form, change)
        if obj.is_approved and not was_previously_approved:
            self.call_flask_api(obj.store_id, request)

    def call_flask_api(self, store_id, request):
        flask_api_url = f"http://127.0.0.1:5000/api/store/approve/{store_id}"
        flask_token = request.session.get('jwt_token')  

        headers = {
            "Authorization": f"Bearer {flask_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.put(flask_api_url, headers=headers)
            if response.status_code != 200:
                print(f"Flask approval failed for store {store_id}: {response.text}")
        except Exception as e:
            print(f"Exception calling Flask API: {e}")

admin.site.register(Store, StoreAdmin)