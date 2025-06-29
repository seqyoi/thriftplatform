from django import forms
from .models import Profile
from .models import Product
import uuid



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'image_file']

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if not instance.product_id:
            instance.product_id = str(uuid.uuid4())  # Generate unique ID
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance
