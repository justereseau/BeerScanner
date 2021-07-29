from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'producer', 'style', 'abv')


class RefillAdmin(admin.ModelAdmin):
    model=Refill
    list_display = ['pk', 'get_client', 'product', 'container', 'tag']
    list_filter = ['user', 'product', 'container', 'tag']

    def get_client(self, obj):
        if obj.user.first_name != '':
            return obj.user.first_name
        else:
            return obj.user
    get_client.short_description = "Client"


class ContainerAdmin(admin.ModelAdmin):
    model = Container
    list_display = ['get_title', 'get_remaining']

    def get_title(self, obj):
        return obj.product.name + " - " + str(obj.capacity) + " L"
    get_title.short_description = 'Name'

    def get_remaining(self, obj):
        refills = Refill.objects.all().filter(product=obj)
        consumed = 0
        for refill in refills:
            consumed += refill.container.capacity
        return str(obj.capacity - consumed) + " L"
    get_remaining.short_description = 'Remaining'

class TapAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_ontap']
    def get_ontap(self, obj):
        return obj.onTap

class ReaderAdmin(admin.ModelAdmin):
    list_display = ['name', 'physical_id', 'get_tap', 'get_ontap']
    def get_tap(self, obj):
        return obj.forTap

    def get_ontap(self, obj):
        if obj.forTap is not None:
            return obj.forTap.onTap
        return None

admin.site.register(Product, ProductAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(PersonalContainer)
admin.site.register(Tag)
admin.site.register(Refill, RefillAdmin)
admin.site.register(Tap, TapAdmin)
admin.site.register(Reader, ReaderAdmin)
