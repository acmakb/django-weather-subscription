import requests
import json
from django.conf import settings
from .models import WeatherData, City


class WeatherService:
    """天气API服务类"""
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.api_url = settings.WEATHER_API_URL
    
    def get_weather_data(self, city_adcode, extensions='all'):
        """
        获取天气数据
        :param city_adcode: 城市adcode
        :param extensions: 气象类型 base/all
        :return: 天气数据字典或None
        """
        try:
            params = {
                'key': self.api_key,
                'city': city_adcode,
                'extensions': extensions,
                'output': 'JSON'
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1' and data.get('infocode') == '10000':
                return data
            else:
                print(f"API返回错误: {data.get('info', '未知错误')}")
                return None
                
        except requests.RequestException as e:
            print(f"请求天气API失败: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析天气API响应失败: {str(e)}")
            return None
    
    def save_weather_data(self, city_adcode):
        """
        获取并保存天气数据到数据库
        :param city_adcode: 城市adcode
        :return: WeatherData对象或None
        """
        try:
            city = City.objects.get(adcode=city_adcode)
        except City.DoesNotExist:
            print(f"城市不存在: {city_adcode}")
            return None
        
        # 获取实况天气
        live_data = self.get_weather_data(city_adcode, 'base')
        if not live_data:
            return None
        
        # 获取预报天气
        forecast_data = self.get_weather_data(city_adcode, 'all')
        
        # 解析实况天气数据
        lives = live_data.get('lives', [])
        if not lives:
            print(f"没有获取到实况天气数据: {city_adcode}")
            return None
        
        live_info = lives[0]
        
        # 创建天气数据记录
        weather_data = WeatherData.objects.create(
            city=city,
            weather=live_info.get('weather', ''),
            temperature=live_info.get('temperature', ''),
            winddirection=live_info.get('winddirection', ''),
            windpower=live_info.get('windpower', ''),
            humidity=live_info.get('humidity', ''),
            reporttime=live_info.get('reporttime', ''),
            forecast_data=forecast_data.get('forecasts', []) if forecast_data else []
        )
        
        return weather_data
    
    def get_weather_for_email(self, city_adcode):
        """
        获取用于邮件发送的天气信息
        :param city_adcode: 城市adcode
        :return: 格式化的天气信息字典
        """
        weather_data = self.save_weather_data(city_adcode)
        if not weather_data:
            return None
        
        # 格式化天气信息
        weather_info = {
            'city_name': weather_data.city.get_full_name(),
            'current': {
                'weather': weather_data.weather,
                'temperature': weather_data.temperature,
                'winddirection': weather_data.winddirection,
                'windpower': weather_data.windpower,
                'humidity': weather_data.humidity,
                'reporttime': weather_data.reporttime
            },
            'forecast': []
        }
        
        # 处理预报数据
        if weather_data.forecast_data:
            for forecast in weather_data.forecast_data:
                if 'casts' in forecast:
                    for cast in forecast['casts']:
                        weather_info['forecast'].append({
                            'date': cast.get('date', ''),
                            'week': cast.get('week', ''),
                            'dayweather': cast.get('dayweather', ''),
                            'nightweather': cast.get('nightweather', ''),
                            'daytemp': cast.get('daytemp', ''),
                            'nighttemp': cast.get('nighttemp', ''),
                            'daywind': cast.get('daywind', ''),
                            'nightwind': cast.get('nightwind', ''),
                            'daypower': cast.get('daypower', ''),
                            'nightpower': cast.get('nightpower', '')
                        })
        
        return weather_info
    
    def test_api_connection(self):
        """测试API连接"""
        # 使用北京的adcode测试
        test_data = self.get_weather_data('110101')
        if test_data:
            print("天气API连接测试成功")
            return True
        else:
            print("天气API连接测试失败")
            return False
