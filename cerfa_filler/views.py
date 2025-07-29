from django.views.generic import DetailView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from weasyprint import HTML
from pypdf import PdfReader, PdfWriter
import io
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from .models import Companies, BeneficiaryOrganization
from .forms import CompaniesForm

from .models import Companies


class Home(TemplateView):
    template_name = "home.html"


class CompaniesCerfa(DetailView):
    template_name = "companies_cerfa.svg"
    model = Companies


class CompaniesCerfaToPdf(DetailView):
    template_name = "companies_cerfa.svg"
    model = Companies

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        company = BeneficiaryOrganization.objects.first()
        context = self.get_context_data(object=self.object, company=company)

        # Generate PDF files from SVG templates
        pdfs = []
        for template in ("companies_1.svg", "companies_2.svg"):
            svg_content = render_to_string(template, context)
            pdf_bytes = HTML(string=svg_content).write_pdf(
                margin_top=0, margin_right=0, margin_bottom=0, margin_left=0
            )
            pdfs.append(
                io.BytesIO(pdf_bytes)
            )  # Use BytesIO to create a file-like object

        # Merge the generated PDF files
        writer = PdfWriter()
        for pdf in pdfs:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)

        filename = f"recu_fiscal_don-{self.object.order_number}.pdf"
        # Create a response with the merged PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Write the merged PDF to the response
        output_pdf = io.BytesIO()  # Create a BytesIO object for the output
        writer.write(output_pdf)
        output_pdf.seek(0)  # Move to the beginning of the BytesIO stream

        response.write(output_pdf.read())  # Write the PDF content to the response

        return response


# views.py


class CompaniesListView(LoginRequiredMixin, ListView):
    model = Companies
    template_name = "company_list.html"
    context_object_name = "companies"


class CompaniesCreateView(LoginRequiredMixin, CreateView):
    model = Companies
    form_class = CompaniesForm
    template_name = "company_form.html"
    success_url = reverse_lazy("cerfa_filler:companies-list")


class CompaniesUpdateView(LoginRequiredMixin, UpdateView):
    model = Companies
    form_class = CompaniesForm
    template_name = "company_form.html"
    success_url = reverse_lazy("cerfa_filler:companies-list")
