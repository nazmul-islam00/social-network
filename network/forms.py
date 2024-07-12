from django import forms

class NewPostForm(forms.Form):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "id": "content",
                "rows": "3"
            }
        )
    )