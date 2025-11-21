from django.contrib import admin
from .models import Announcement,Tag #Tag追加

admin.site.register(Announcement)
admin.site.register(Tag) # Tagを登録