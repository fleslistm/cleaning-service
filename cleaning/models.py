from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class RoomType(models.Model):
    name = models.CharField("Тип помещения", max_length=100, unique=True)
    coefficient = models.DecimalField("Коэффициент цены", max_digits=5, decimal_places=2, default=1)
    def __str__(self): return self.name
    class Meta: verbose_name = "Тип помещения"; verbose_name_plural = "Типы помещений"

class Service(models.Model):
    name = models.CharField("Название услуги", max_length=140)
    description = models.TextField("Описание", blank=True)
    price_per_m2 = models.DecimalField("Цена за м²", max_digits=9, decimal_places=2)
    active = models.BooleanField("Активна", default=True)
    room_types = models.ManyToManyField(RoomType, blank=True, related_name="services", verbose_name="Типы помещений")
    def __str__(self): return self.name
    class Meta: ordering = ["name"]; verbose_name = "Услуга"; verbose_name_plural = "Услуги"

class Team(models.Model):
    name = models.CharField("Название бригады", max_length=100, unique=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    active = models.BooleanField("Активна", default=True)
    def __str__(self): return self.name
    class Meta: verbose_name = "Бригада"; verbose_name_plural = "Бригады"

class CleaningOrder(models.Model):
    STATUS = [("new","Новый"),("confirmed","Подтверждён"),("progress","В работе"),("done","Завершён"),("cancelled","Отменён")]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cleaning_orders", verbose_name="Заказчик")
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, verbose_name="Тип помещения")
    services = models.ManyToManyField(Service, through="OrderService", related_name="orders")
    area = models.PositiveIntegerField("Площадь, м²", validators=[MinValueValidator(1), MaxValueValidator(10000)])
    address = models.CharField("Адрес", max_length=255)
    scheduled_at = models.DateTimeField("Дата и время уборки")
    phone = models.CharField("Телефон", max_length=20)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=16, choices=STATUS, default="new")
    total = models.DecimalField("Итого, ₽", max_digits=11, decimal_places=2, default=0)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    def __str__(self): return f"Заказ №{self.pk}"
    class Meta: ordering = ["-created_at"]; verbose_name = "Заказ"; verbose_name_plural = "Заказы"

class OrderService(models.Model):
    order = models.ForeignKey(CleaningOrder, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    price = models.DecimalField("Цена на момент заказа", max_digits=9, decimal_places=2)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["order","service"], name="uniq_order_service")]
        verbose_name = "Услуга заказа"; verbose_name_plural = "Услуги заказа"
    def __str__(self): return f"{self.order} — {self.service}"

class Review(models.Model):
    order = models.OneToOneField(CleaningOrder, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveSmallIntegerField("Оценка", validators=[MinValueValidator(1),MaxValueValidator(5)])
    text = models.TextField("Отзыв", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Отзыв {self.rating}/5"

class Invoice(models.Model):
    order = models.OneToOneField(CleaningOrder, on_delete=models.CASCADE, related_name="invoice")
    number = models.CharField("Номер счёта", max_length=30, unique=True)
    amount = models.DecimalField("Сумма", max_digits=11, decimal_places=2)
    paid = models.BooleanField("Оплачен вручную", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.number
