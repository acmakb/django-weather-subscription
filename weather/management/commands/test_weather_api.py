from django.core.management.base import BaseCommand
from weather.services import WeatherService
from weather.models import City


class Command(BaseCommand):
    help = '测试天气API连接和数据获取'

    def add_arguments(self, parser):
        parser.add_argument(
            '--city',
            type=str,
            default='110101',  # 北京东城区
            help='城市adcode'
        )

    def handle(self, *args, **options):
        city_adcode = options['city']
        
        weather_service = WeatherService()
        
        # 测试API连接
        self.stdout.write("测试天气API连接...")
        if weather_service.test_api_connection():
            self.stdout.write(self.style.SUCCESS("API连接测试成功"))
        else:
            self.stdout.write(self.style.ERROR("API连接测试失败"))
            return
        
        # 测试获取指定城市天气
        self.stdout.write(f"获取城市 {city_adcode} 的天气数据...")
        
        try:
            city = City.objects.get(adcode=city_adcode)
            self.stdout.write(f"城市: {city.get_full_name()}")
        except City.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"城市不存在: {city_adcode}"))
            return
        
        # 获取天气数据
        weather_info = weather_service.get_weather_for_email(city_adcode)
        
        if weather_info:
            self.stdout.write(self.style.SUCCESS("天气数据获取成功:"))
            self.stdout.write(f"城市: {weather_info['city_name']}")
            self.stdout.write(f"当前天气: {weather_info['current']['weather']}")
            self.stdout.write(f"当前温度: {weather_info['current']['temperature']}°C")
            self.stdout.write(f"风向: {weather_info['current']['winddirection']}")
            self.stdout.write(f"风力: {weather_info['current']['windpower']}级")
            self.stdout.write(f"湿度: {weather_info['current']['humidity']}%")
            self.stdout.write(f"更新时间: {weather_info['current']['reporttime']}")
            
            if weather_info['forecast']:
                self.stdout.write("\n未来天气预报:")
                for i, forecast in enumerate(weather_info['forecast'][:3]):  # 显示前3天
                    self.stdout.write(f"  {forecast['date']} {forecast['week']}: "
                                    f"{forecast['dayweather']} "
                                    f"{forecast['nighttemp']}°C~{forecast['daytemp']}°C")
        else:
            self.stdout.write(self.style.ERROR("天气数据获取失败"))
