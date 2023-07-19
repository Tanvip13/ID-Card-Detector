from django import forms
from recognition.models import Recognition


class RecognitionNameForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "please enter your name"}),
        max_length=100
    )
    class Meta:
        model = Recognition
        fields = ('name',)


class RecognitionImageForm(forms.ModelForm):
    class Meta:
        model = Recognition
        fields = ('id_image',)
