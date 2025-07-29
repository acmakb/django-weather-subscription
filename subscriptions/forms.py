from django import forms
from weather.models import City
from .models import Subscription


class SubscriptionForm(forms.ModelForm):
    """订阅表单"""
    province = forms.ModelChoiceField(
        queryset=City.objects.filter(level=1),
        empty_label="请选择省份",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'province-select'
        }),
        label='省份'
    )
    
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        empty_label="请选择城市",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'city-select'
        }),
        label='城市'
    )
    
    district = forms.ModelChoiceField(
        queryset=City.objects.none(),
        empty_label="请选择区县",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'district-select'
        }),
        label='区县',
        required=False
    )

    class Meta:
        model = Subscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入接收天气信息的邮箱'
            })
        }
        labels = {
            'email': '接收邮箱'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 如果表单有数据，动态加载城市和区县选项
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['city'].queryset = City.objects.filter(
                    parent_id=province_id, level=2
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['district'].queryset = City.objects.filter(
                    parent_id=city_id, level=3
                ).order_by('name')
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        province = cleaned_data.get('province')
        city = cleaned_data.get('city')
        district = cleaned_data.get('district')
        
        # 确定最终选择的城市
        if district:
            final_city = district
        elif city:
            final_city = city
        elif province:
            final_city = province
        else:
            raise forms.ValidationError('请至少选择一个地区')
        
        cleaned_data['final_city'] = final_city
        return cleaned_data


class CitySearchForm(forms.Form):
    """城市搜索表单"""
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索城市名称...',
            'autocomplete': 'off'
        }),
        label='搜索城市'
    )
