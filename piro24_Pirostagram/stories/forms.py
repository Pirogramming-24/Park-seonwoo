from django import forms
from .models import Story, StoryImage

class MultipleFileInput(forms.ClearableFileInput):
    """다중 파일 업로드를 지원하는 커스텀 위젯"""
    allow_multiple_selected = True
    
    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)

class MultipleFileField(forms.FileField):
    """다중 파일을 처리하는 커스텀 필드"""
    widget = MultipleFileInput
    
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class StoryForm(forms.ModelForm):
    # 여러 이미지를 받기 위한 필드
    images = MultipleFileField(
        label='스토리 이미지들',
        required=True
    )
    
    class Meta:
        model = Story
        fields = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
        self.fields['images'].help_text = '여러 장의 이미지를 선택할 수 있습니다.'