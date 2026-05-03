from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class Candidate(models.Model):
    id = models.AutoField(primary_key=True)

    user_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)

    answers_text = models.TextField(verbose_name="Текст ответов")
    ai_score = models.IntegerField(verbose_name="Оценка ИИ")
    ai_summary = models.TextField(null=True, blank=True, verbose_name="Резюме ИИ")

    ai_probability = models.FloatField(default=0.0, verbose_name="Вероятность")

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.full_name or self.username} - Score: {self.ai_score}"

    class Meta:
        verbose_name = "Кандидат"
        verbose_name_plural = "Кандидаты"