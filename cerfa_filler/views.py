import base64
import io

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from pypdf import PdfReader, PdfWriter
from weasyprint import HTML

from .forms import CompaniesForm
from .models import BeneficiaryOrganization, Companies


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
        context = self.get_context_data()

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
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{filename}"'  # noqa: E702

        # Write the merged PDF to the response
        output_pdf = io.BytesIO()  # Create a BytesIO object for the output
        writer.write(output_pdf)
        output_pdf.seek(0)  # Move to the beginning of the BytesIO stream

        response.write(
            output_pdf.read()
        )  # Write the PDF content to the response

        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        company = BeneficiaryOrganization.objects.first()
        data["company"] = company
        if company.sign_file:
            with open(company.sign_file.path, "rb") as sign_file:
                print(sign_file)
                data["sign_file"] = base64.b64encode(sign_file.read()).decode(
                    "utf-8"
                )
        return data


# class CompaniesCerfaToPdf(DetailView):
#     template_name = "companies_2.svg"
#     model = Companies

#     # def get(self, request, *args, **kwargs):
#     #     self.context = self.get_context_data()
#     #     company = BeneficiaryOrganization.objects.first()
#     #     context = self.get_context_data(object=self.object, company=company)
#     #     return context

#     # def get_context_data(self, **kwargs):
#     #     self.object = self.get_object()
#     #     company = BeneficiaryOrganization.objects.first()
#     #     context = self.get_context_data(object=self.object, company=company)
#     #     return context
#     #     return super().get_context_data(**kwargs)

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         company = BeneficiaryOrganization.objects.first()
#         data['company'] = company
#         with open(company.sign_file.path, 'rb') as sign_file:
#             print(sign_file)
#             data['sign_file'] = base64.b64encode(sign_file.read()).decode('utf-8')
#         return data


# views.py


@method_decorator(
    permission_required("cerfa_filler.view_companies"), name="dispatch"
)
class CompaniesListView(LoginRequiredMixin, ListView):
    model = Companies
    template_name = "company_list.html"
    context_object_name = "companies"


@method_decorator(
    permission_required("cerfa_filler.create_companies"), name="dispatch"
)
class CompaniesCreateView(LoginRequiredMixin, CreateView):
    model = Companies
    form_class = CompaniesForm
    template_name = "company_form.html"
    success_url = reverse_lazy("cerfa_filler:companies-list")


@method_decorator(
    permission_required("cerfa_filler.change_companies"), name="dispatch"
)
class CompaniesUpdateView(LoginRequiredMixin, UpdateView):
    model = Companies
    form_class = CompaniesForm
    template_name = "company_form.html"
    success_url = reverse_lazy("cerfa_filler:companies-list")


@method_decorator(
    permission_required("cerfa_filler.change_validation"), name="dispatch"
)
class CompaniesUpdateValidDateView(LoginRequiredMixin, View):
    def post(self, request):
        selected_uuids = request.POST.getlist("selected_companies")
        # Assuming you want to set the valid_date to the current date
        valid_date = timezone.now()

        # Update the valid_date for selected companies
        Companies.objects.filter(uuid__in=selected_uuids).update(
            valid_date=valid_date
        )

        return redirect(
            "cerfa_filler:companies-list"
        )  # Redirect to the companies list page
