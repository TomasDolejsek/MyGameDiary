from django.db import models


# *********************************** Form Template Model Views ************************************


class FormTemplate(models.Model):
    # account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    configuration = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name}"
