from django import forms    

class CarregarCSVForm(forms.Form):
    arquivo_csv = forms.FileField()