import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView, View, ListView

from editor_app.models import FormTemplate


# **************************************** Templates Views *****************************************

class TemplateListView(ListView):
    model = FormTemplate
    template_name = 'template-list.html'
    context_object_name = 'templates'
    ordering = ['-updated_at']


# ***************************************** Editor Views *******************************************

class NewTemplateView(TemplateView):
    template_name = 'editor.html'


class EditTemplateView(TemplateView):
    template_name = 'editor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = FormTemplate.objects.filter(pk=self.kwargs['template_id']).first()
        return context


class SaveTemplateView(View):
    def post(self, request, template_id=None):
        try:
            data = json.loads(request.body)
            if template_id:
                # Update existing template
                template = FormTemplate.objects.get(id=template_id)
                template.description = data['description']
                template.name = data['name']
                template.configuration = data
                template.save()
            else:
                # Create a new template
                template = FormTemplate.objects.create(
                    name=data['name'],
                    configuration=data
                )

            return JsonResponse({
                'status': 'success',
                'template_id': template.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


class LoadTemplateView(View):
    def get(self, request, template_id):
        try:
            template = get_object_or_404(FormTemplate, id=template_id)
            return JsonResponse({
                'name': template.name,
                'description': template.description,
                'elements': template.configuration['elements'],
                'elementCounts': template.configuration['elementCounts']
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
