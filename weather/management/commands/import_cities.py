import pandas as pd
from django.core.management.base import BaseCommand
from weather.models import City


class Command(BaseCommand):
    help = '导入城市数据从Excel文件'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='AMap_adcode_citycode.xlsx',
            help='Excel文件路径'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            self.stdout.write(f"读取到 {len(df)} 条数据")
            
            # 清空现有数据
            City.objects.all().delete()
            self.stdout.write("已清空现有城市数据")
            
            # 创建城市层级映射
            city_map = {}
            
            # 第一遍：创建所有城市记录
            for index, row in df.iterrows():
                name = row['中文名']
                adcode = str(row['adcode'])
                citycode = str(row['citycode']) if pd.notna(row['citycode']) else None
                
                # 判断城市级别
                level = self.get_city_level(adcode)
                
                city = City.objects.create(
                    name=name,
                    adcode=adcode,
                    citycode=citycode,
                    level=level
                )
                
                city_map[adcode] = city
                
                if index % 100 == 0:
                    self.stdout.write(f"已处理 {index + 1} 条数据")
            
            # 第二遍：设置父级关系
            for adcode, city in city_map.items():
                parent_adcode = self.get_parent_adcode(adcode)
                if parent_adcode and parent_adcode in city_map:
                    city.parent = city_map[parent_adcode]
                    city.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'成功导入 {len(city_map)} 个城市数据')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'导入失败: {str(e)}')
            )

    def get_city_level(self, adcode):
        """根据adcode判断城市级别"""
        if adcode == '100000':
            return 0  # 国家
        elif adcode.endswith('0000'):
            return 1  # 省级
        elif adcode.endswith('00'):
            return 2  # 市级
        else:
            return 3  # 区县级

    def get_parent_adcode(self, adcode):
        """获取父级adcode"""
        if adcode == '100000':
            return None  # 国家级没有父级
        elif adcode.endswith('0000'):
            return '100000'  # 省级的父级是国家
        elif adcode.endswith('00'):
            # 市级的父级是省级
            return adcode[:2] + '0000'
        else:
            # 区县级的父级是市级
            return adcode[:4] + '00'
