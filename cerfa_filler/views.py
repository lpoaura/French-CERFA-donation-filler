import base64
import io
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import FieldError
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

from .forms import (
    BaseFilterForm,
    CompaniesFilterForm,
    CompaniesForm,
    IndividualFilterForm,
    PrivateIndividualForm,
)
from .models import BeneficiaryOrganization, Companies, PrivateIndividual

# HOME


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company_max_year = (
            Companies.objects.values("date_start__year")
            .distinct()
            .order_by("-date_start")
            .first()
        )
        context["company_max_year"] = company_max_year.get(
            "date_start__year", datetime.now().year
        )

        individual_max_year = (
            PrivateIndividual.objects.values("date_start__year")
            .distinct()
            .order_by("-date_start")
            .first()
        )
        context["individual_max_year"] = individual_max_year.get(
            "date_start__year", datetime.now().year
        )
        return context


# COMPANIES


class BaseListView(ListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.GET.get("year")
        declarative_structure = self.request.GET.get("declarative_structure")
        validation = self.request.GET.get("validation")

        if year:
            queryset = queryset.filter(date_start__year=year)
        if declarative_structure:
            queryset = queryset.filter(
                declarative_structure=declarative_structure
            )
        if validation:
            try:
                queryset = queryset.filter(
                    valid_date__isnull=(validation.lower() == "false")
                )
            except SyntaxError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterForm"] = BaseFilterForm(
            self.request.GET, model=self.model
        )
        return context


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


@method_decorator(
    permission_required("cerfa_filler.view_companies"), name="dispatch"
)
class CompaniesListView(LoginRequiredMixin, BaseListView):
    model = Companies
    template_name = "company_list.html"
    context_object_name = "companies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterForm"] = CompaniesFilterForm(
            self.request.GET, model=self.model
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        donation_kind = self.request.GET.get("donation_kind")
        if donation_kind:
            print("donation kind", donation_kind)
            try:
                if donation_kind == "cash":
                    queryset = queryset.filter(
                        cash_donation__isnull=False, cash_donation__gt=0
                    )
                if donation_kind == "nature":
                    queryset = queryset.filter(
                        inkind_donation__isnull=False, inkind_donation__gt=0
                    )
            except FieldError:
                pass
        return queryset


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


# INDIVIDUALS


@method_decorator(
    permission_required("cerfa_filler.view_private_individuals"),
    name="dispatch",
)
class PrivateIndividualListView(LoginRequiredMixin, BaseListView):
    model = PrivateIndividual
    template_name = "private_individual_list.html"
    context_object_name = "individuals"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterForm"] = IndividualFilterForm(
            self.request.GET, model=self.model
        )
        return context


@method_decorator(
    permission_required("cerfa_filler.create_private_individuals"),
    name="dispatch",
)
class PrivateIndividualCreateView(LoginRequiredMixin, CreateView):
    model = PrivateIndividual
    form_class = PrivateIndividualForm
    template_name = "private_individual_form.html"
    success_url = reverse_lazy("cerfa_filler:private-individual-list")


@method_decorator(
    permission_required("cerfa_filler.change_private_individuals"),
    name="dispatch",
)
class PrivateIndividualUpdateView(LoginRequiredMixin, UpdateView):
    model = PrivateIndividual
    form_class = PrivateIndividualForm
    template_name = "private_individual_form.html"
    success_url = reverse_lazy("cerfa_filler:private-individual-list")


@method_decorator(
    permission_required("cerfa_filler.change_validation"), name="dispatch"
)
class PrivateIndividualUpdateValidDateView(LoginRequiredMixin, View):
    def post(self, request):
        selected_uuids = request.POST.getlist("selected_individuals")
        # Assuming you want to set the valid_date to the current date
        valid_date = timezone.now()

        # Update the valid_date for selected PrivateIndividual
        PrivateIndividual.objects.filter(uuid__in=selected_uuids).update(
            valid_date=valid_date
        )

        return redirect(
            "cerfa_filler:private-individual-list"
        )  # Redirect to the PrivateIndividual list page


class PrivateIndividualCerfaToPdf(DetailView):
    template_name = "companies_cerfa.svg"
    model = PrivateIndividual

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
