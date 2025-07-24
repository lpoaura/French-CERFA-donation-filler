from django.views.generic import DetailView
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from pypdf import PdfReader, PdfWriter
import io

from .models import Companies


class CompaniesCerfa(DetailView):
    template_name = "companies_cerfa.svg"
    model = Companies


class CompaniesCerfaToPdf(DetailView):
    template_name = "companies_cerfa.svg"
    model = Companies

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # Generate PDF files from SVG templates
        pdfs = []
        for template in ("companies_1.svg", "companies_2.svg"):
            svg_content = render_to_string(template, context)
            pdf_bytes = HTML(string=svg_content).write_pdf()
            pdfs.append(io.BytesIO(pdf_bytes))  # Use BytesIO to create a file-like object

        # Merge the generated PDF files
        writer = PdfWriter()
        for pdf in pdfs:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)

        # Create a response with the merged PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="output.pdf"'
        
        # Write the merged PDF to the response
        output_pdf = io.BytesIO()  # Create a BytesIO object for the output
        writer.write(output_pdf)
        output_pdf.seek(0)  # Move to the beginning of the BytesIO stream

        response.write(output_pdf.read())  # Write the PDF content to the response

        return response