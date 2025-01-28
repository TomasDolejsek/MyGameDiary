from django.urls import path

from editor_app.views import TemplateListView, NewTemplateView, EditTemplateView, SaveTemplateView, LoadTemplateView

app_name = 'editor'

urlpatterns = [
    # templates views
    path('', TemplateListView.as_view(), name='template_list'),

    # editor views
    path('new-template/', NewTemplateView.as_view(), name='new_template'),
    path('edit-template/<int:template_id>/', EditTemplateView.as_view(), name='edit_template'),
    path('save-template/<int:template_id>/', SaveTemplateView.as_view(), name='save_template'),
    path('save-template/', SaveTemplateView.as_view(), name='save_new_template'),
    path('load-template/<int:template_id>/', LoadTemplateView.as_view(), name='load_template'),
]
