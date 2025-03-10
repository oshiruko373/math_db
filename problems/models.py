from django.db import models

class ThoughtProcess(models.Model):
    process = models.TextField()
    related_processes = models.ManyToManyField('self', symmetrical=False, blank=True)

    def __str__(self):
        return self.process[:50]

class Tag(models.Model):
    name = models.CharField(max_length=100)  # TextFieldから変更
    def __str__(self):
        return self.name

class Problem(models.Model):
    source_year = models.IntegerField()  # DateTimeFieldからIntegerFieldへ変更
    source_university = models.CharField(max_length=255)  # TextFieldから変更
    source_faculty = models.CharField(max_length=255)  # TextFieldから変更
    boxURL = models.URLField(null=True, blank=True)
    difficulty = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='problems', blank=True)  # フィールド名を変更
    thought_processes = models.ManyToManyField(ThoughtProcess, blank=True, related_name="problems")
    good_points = models.TextField(null=True, blank=True)  # `良い点` の新しいフィールド名
    usage_location = models.TextField(null=True, blank=True)  # `扱う場所` の新しいフィールド名

    def __str__(self):
        return f"{self.source_university} {self.source_year}"
