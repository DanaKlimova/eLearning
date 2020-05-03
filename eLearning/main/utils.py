from io import BytesIO
import os
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.contrib.staticfiles import finders

from weasyprint import HTML, CSS

def render_to_pdf(template_src, request, context_dict={}):
    template = get_template(template_src)
    rendered_html = template.render(context_dict)
    base_url=request.build_absolute_uri()
    html = HTML(string=rendered_html, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf(stylesheets=[CSS(finders.find('courses/css/certificate.css'))])
    return pdf_file