from django.contrib import admin
from .models import City, WeatherData


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """城市管理"""
    list_display = ('name', 'adcode', 'citycode', 'level', 'parent', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('name', 'adcode', 'citycode')
    ordering = ('level', 'name')
    list_per_page = 50

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'adcode', 'citycode')
        }),
        ('层级关系', {
            'fields': ('parent', 'level')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    """天气数据管理"""
    list_display = ('city', 'weather', 'temperature', 'winddirection', 'windpower', 'humidity', 'created_at')
    list_filter = ('weather', 'created_at')
    search_fields = ('city__name', 'weather')
    ordering = ('-created_at',)
    list_per_page = 50

    fieldsets = (
        ('基本信息', {
            'fields': ('city', 'weather', 'temperature')
        }),
        ('风力信息', {
            'fields': ('winddirection', 'windpower')
        }),
        ('其他信息', {
            'fields': ('humidity', 'reporttime')
        }),
        ('预报数据', {
            'fields': ('forecast_data',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)
