from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

from weasyprint import HTML, CSS

def render_to_pdf(template_src, request, context_dict={}):
    template = get_template(template_src)
    rendered_html = template.render(context_dict)

    base_url=request.build_absolute_uri()

    print(settings.BASE_DIR)
    # html = HTML(string=html_string, base_url=request.build_absolute_uri())

    # pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=[CSS('/home/dana/apps/eLearning_System/eLearning/eLearning/courses/static/courses/css/certificate.css')])
    pdf_file = HTML(string=rendered_html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS('/home/dana/apps/eLearning_System/eLearning/eLearning/courses/static/courses/css/certificate.css')])

    http_response = HttpResponse(pdf_file, content_type='application/pdf')
    http_response['Content-Disposition'] = 'filename="report.pdf"'

    return pdf_file

    # result = BytesIO()
    # pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    # if not pdf.err:
    #     return HttpResponse(result.getvalue(), content_type='application/pdf')
    # return None