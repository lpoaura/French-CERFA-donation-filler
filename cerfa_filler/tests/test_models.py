from django.test import TestCase
from ..models import DeclarativeStructure, CompanyLegalForms, BeneficiaryOrganization, Companies
from django.utils import timezone
import urllib.parse
from django.conf import settings
from django.urls import reverse

class DeclarativeStructureTest(TestCase):
    def setUp(self):
        self.declarative_structure = DeclarativeStructure.objects.create(label="Test Structure")

    def test_declarative_structure_creation(self):
        self.assertEqual(self.declarative_structure.label, "Test Structure")

    def test_declarative_structure_string_representation(self):
        self.assertEqual(str(self.declarative_structure), "Test Structure")


class CompanyLegalFormsTest(TestCase):
    def setUp(self):
        self.legal_form = CompanyLegalForms.objects.create(code="LLC", label="Limited Liability Company")

    def test_company_legal_form_creation(self):
        self.assertEqual(self.legal_form.code, "LLC")
        self.assertEqual(self.legal_form.label, "Limited Liability Company")

    def test_company_legal_form_string_representation(self):
        self.assertEqual(str(self.legal_form), "Limited Liability Company")


class BeneficiaryOrganizationTest(TestCase):
    def setUp(self):
        self.beneficiary = BeneficiaryOrganization.objects.create(
            label="Test Beneficiary",
            repository_code="12345",
            postal_code="75001",
            municipality="Paris",
        )

    def test_beneficiary_creation(self):
        self.assertEqual(self.beneficiary.label, "Test Beneficiary")
        self.assertEqual(self.beneficiary.repository_code, "12345")
        self.assertEqual(self.beneficiary.postal_code, "75001")
        self.assertEqual(self.beneficiary.municipality, "Paris")

    def test_beneficiary_string_representation(self):
        self.assertEqual(str(self.beneficiary), "Test Beneficiary")


class CompaniesTest(TestCase):
    def setUp(self):
        self.declarative_structure = DeclarativeStructure.objects.create(label="Test Structure")
        self.company = Companies.objects.create(
            label="Test Company",
            repository_code="54321",
            postal_code="75002",
            municipality="Paris",
            declarative_structure=self.declarative_structure,
            cash_donation=100.00,
            inkind_donation=50.00
        )

    def test_companies_creation(self):
        self.assertEqual(self.company.label, "Test Company")
        self.assertEqual(self.company.repository_code, "54321")
        self.assertEqual(self.company.postal_code, "75002")
        self.assertEqual(self.company.municipality, "Paris")
        self.assertEqual(self.company.cash_donation, 100.00)
        self.assertEqual(self.company.inkind_donation, 50.00)

    def test_total_donation(self):
        self.assertEqual(self.company.total_donation, 150.00)

    def test_total_donation_as_text(self):
        self.assertIsNotNone(self.company.total_donation_as_text)

    def test_order_number(self):
        self.assertEqual(self.company.order_number, f"{self.company.year}-PM-{self.company.order}")

    def test_mailto_property(self):
        self.company.email = "test@example.com"
        formattedSubject="Tax receipt for your donation"
        formattedLink = f"{settings.SITE}{reverse('cerfa_filler:companies-cerfa-pdf', kwargs={'pk': self.company.uuid})}"
        formattedBody=urllib.parse.quote(f'Hello,\n\nPlease find below a link to download your tax receipt for your donation.\n\n{formattedLink}\n\nSincerely')
        expected_mailto = f"mailto:test@example.com?subject={formattedSubject}&body={formattedBody}"
        self.assertEqual(self.company.mailto, expected_mailto)

    def test_save_method(self):
        self.company.save()
        self.assertIsNotNone(self.company.order)  # Ensure order is set after save
