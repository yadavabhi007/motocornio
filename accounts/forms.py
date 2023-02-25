from django import forms
from .models import ResponsiveLetter
from jsignature.widgets import JSignatureWidget
from jsignature.forms import JSignatureField

class SignatureForm(forms.ModelForm):
    signature = JSignatureField(widget=JSignatureWidget(jsignature_attrs={'color': '#e0b642', 'height': '200px'}))
    class Meta:
        model = ResponsiveLetter
        fields = ['signature']