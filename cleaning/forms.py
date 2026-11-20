from django import forms
from django.core.validators import RegexValidator
from .models import CleaningOrder, Review, Service
phone_validator = RegexValidator(r"^\+?[0-9 ()-]{10,20}$", "Введите корректный номер телефона.")
class OrderForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(queryset=Service.objects.filter(active=True), widget=forms.CheckboxSelectMultiple, required=True, label="Услуги")
    phone = forms.CharField(validators=[phone_validator], label="Телефон")
    class Meta:
        model = CleaningOrder
        fields = ["room_type","area","address","scheduled_at","phone","comment","services"]
        widgets = {"scheduled_at": forms.DateTimeInput(attrs={"type":"datetime-local"}), "comment":forms.Textarea(attrs={"rows":3})}
    def clean_area(self):
        area=self.cleaned_data["area"]
        if area < 10: raise forms.ValidationError("Минимальная площадь — 10 м².")
        return area
class ReviewForm(forms.ModelForm):
    class Meta:
        model=Review
        fields=["rating","text"]
