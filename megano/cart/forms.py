from django import forms

from catalog.models import Stock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ("seller", "product", "quantity", "price")
