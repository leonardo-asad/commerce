from django import forms
from .models import Listing, Bid

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

class BidForm(forms.Form):
    bid = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}))

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
