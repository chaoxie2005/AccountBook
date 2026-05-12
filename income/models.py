from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Income(models.Model):
    amount = models.FloatField(verbose_name="金额", null=False, blank=False)
    date = models.DateField(verbose_name='日期', null=False, blank=False)
    description = models.TextField(verbose_name='收入描述', default="", null=False)
    category = models.CharField(verbose_name='分类', max_length=255, null=False, blank=False)
    owner = models.ForeignKey(verbose_name='关联账户', to=User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner} 的收入记录：{self.amount} 元，类别：{self.category}，日期：{self.date}"

    class Meta:
        verbose_name = '收入记录'
        verbose_name_plural = verbose_name


class IncomeCategory(models.Model):
    name = models.CharField(verbose_name='分类名称', max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '收入类型'
        verbose_name_plural = verbose_name
