from django import forms
from .models import Lab, Equipment, EquipmentCategory, EquipmentSubCategory, LabBooking


class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ['name', 'location', 'description', 'capacity', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = 3


class EquipmentCategoryForm(forms.ModelForm):
    class Meta:
        model = EquipmentCategory
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = 3


class EquipmentSubCategoryForm(forms.ModelForm):
    class Meta:
        model = EquipmentSubCategory
        fields = ['name', 'category', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = 3


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'lab', 'category', 'sub_category', 'status', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'image':
                field.widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = 3
        self.fields['sub_category'].queryset = EquipmentSubCategory.objects.none()
        if self.instance.pk and self.instance.category:
            self.fields['sub_category'].queryset = EquipmentSubCategory.objects.filter(category=self.instance.category)
        elif 'category' in self.data:
            try:
                cat_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = EquipmentSubCategory.objects.filter(category_id=cat_id)
            except (ValueError, TypeError):
                pass


class LabBookingForm(forms.ModelForm):
    class Meta:
        model = LabBooking
        fields = ['equipment', 'lab_unit', 'purpose', 'quantity_booked', 'start_date', 'end_date', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['start_date'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local', 'class': 'form-control'
        })
        self.fields['end_date'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local', 'class': 'form-control'
        })
        self.fields['purpose'].widget.attrs['rows'] = 3
        self.fields['notes'].widget.attrs['rows'] = 2
        self.fields['equipment'].queryset = Equipment.objects.filter(status='available')
