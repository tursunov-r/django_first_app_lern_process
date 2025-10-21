from django import forms
from shopapp.models import Product, Order


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductForm(forms.ModelForm):
    images = MultipleFileField(
        widget=MultipleFileInput(attrs={"multiple": True}),
        label="Add other images",
        required=False,
    )

    class Meta:
        model = Product
        fields = ("name", "price", "description", "discount", "preview")


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только неархивированные продукты
        self.fields["products"].queryset = Product.objects.filter(archived=False)


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
