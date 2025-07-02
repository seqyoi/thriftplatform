from django import forms
from .models import Profile
from .models import Product
import uuid



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio']

from django import forms
from .models import Product
import uuid

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'image_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your product...'}),
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Red Cotton Jacket'}),
            'price': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'description': 'Try to add at least 10 words to help buyers find your product easily.',
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if not instance.product_id:
            instance.product_id = str(uuid.uuid4())  # Ensure unique product ID
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance
