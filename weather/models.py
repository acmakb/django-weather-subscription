from django.db import models


class City(models.Model):
    """城市数据模型"""
    name = models.CharField(max_length=100, verbose_name="城市名称")
    adcode = models.CharField(max_length=20, unique=True, verbose_name="区域编码")
    citycode = models.CharField(max_length=20, null=True, blank=True, verbose_name="城市编码")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="上级城市")
    level = models.IntegerField(default=0, verbose_name="级别")  # 0:国家, 1:省, 2:市, 3:区县
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "城市"
        verbose_name_plural = "城市"
        ordering = ['level', 'name']

    def __str__(self):
        return self.name

    def get_full_name(self):
        """获取完整地址名称"""
        if self.parent:
            return f"{self.parent.get_full_name()} {self.name}"
        return self.name


class WeatherData(models.Model):
    """天气数据模型"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="城市")
    weather = models.CharField(max_length=50, verbose_name="天气现象")
    temperature = models.CharField(max_length=10, verbose_name="实时气温")
    winddirection = models.CharField(max_length=20, verbose_name="风向")
    windpower = models.CharField(max_length=10, verbose_name="风力级别")
    humidity = models.CharField(max_length=10, verbose_name="空气湿度")
    reporttime = models.CharField(max_length=50, verbose_name="数据发布时间")

    # 预报数据
    forecast_data = models.JSONField(null=True, blank=True, verbose_name="预报数据")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "天气数据"
        verbose_name_plural = "天气数据"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.city.name} - {self.weather} - {self.temperature}°C"
