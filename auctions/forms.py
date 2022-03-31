from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title','description','image','price','category')

        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
