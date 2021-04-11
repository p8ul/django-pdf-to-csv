from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.views.generic.edit import FormView
import csv

from .utils import process_text, csv_headers

class UploadForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': False}))

    def handle_uploaded_file(self):
        # print(self, '*' * 23)
        pass


class HomeView(FormView):
    template_name = "home/index.html"

    form_class = UploadForm
    success_url = '/thanks/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UploadForm()
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file')
        if form.is_valid():
            for f in files:
                with open('output.pdf', 'wb+') as output:
                    output.write(f.read())
                processed_data = process_text('')

                response = HttpResponse(content_type='text/csv', )
                response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

                writer = csv.writer(response)
                writer.writerow(csv_headers)
                for item in processed_data.get('courses'):
                    course = item.get('course')
                    writer.writerow([
                        processed_data.get('academic_year'),
                        processed_data.get('degree'),
                        processed_data.get('college_from'),
                        processed_data.get('college_to'),
                        course.get('title'),
                        course.get('code'),
                        course.get('hours'),
                        item.get('conditional')
                    ])
                return response

            form.handle_uploaded_file()
            return HttpResponse({'name': "succes"})
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.handle_uploaded_file()
        return super().form_valid(form)
