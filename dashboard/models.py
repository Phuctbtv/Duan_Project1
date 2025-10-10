from django.db import models

# Create your models here.

class DashboardStats(models.Model):
    stat_date = models.DateField(unique=True)
    total_customers = models.IntegerField(default=0)
    active_contracts = models.IntegerField(default=0)
    monthly_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Thống kê dashboard'
        verbose_name_plural = 'Thống kê dashboard'

    def __str__(self):
        return f"Stats for {self.stat_date}"