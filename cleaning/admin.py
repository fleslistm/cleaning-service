from django.contrib import admin
from .models import RoomType,Service,Team,CleaningOrder,OrderService,Review,Invoice
admin.site.register([RoomType,Service,Team,CleaningOrder,OrderService,Review,Invoice])
