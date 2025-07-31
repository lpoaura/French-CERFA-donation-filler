from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from ..models import DeclarativeStructure, Companies, BeneficiaryOrganization
from ..forms import CompaniesForm

class CompaniesViewTest(TestCase):
    fixtures = ["group.json"]

    def setUp(self):
        self.client = Client()
        # Create a user and log them in
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user.groups.set(Group.objects.all())

        self.client.login(username='testuser', password='testpassword')

        # Create a DeclarativeStructure instance
        self.declarative_structure = DeclarativeStructure.objects.create(label="Test Structure")
        self.beneficiary = BeneficiaryOrganization.objects.create(
            label="Test Beneficiary",
            repository_code="12345",
            postal_code="75001",
            municipality="Paris",
        )

        # Create a Companies instance
        self.company = Companies.objects.create(
            label="Test Company",
            repository_code="54321",
            postal_code="75002",
            municipality="Paris",
            declarative_structure=self.declarative_structure,
            cash_donation=100.00,
            inkind_donation=50.00
        )

    def test_authenticate_user_using_login_method(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Check if the user is authenticated
        response = self.client.get(reverse('cerfa_filler:companies-create'))
        print(response.headers)
        self.assertEqual(response.status_code, 200)

    def test_companies_list_view(self):
        response = self.client.get(reverse('cerfa_filler:companies-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'company_list.html')
        self.assertContains(response, "Test Company")

    def test_companies_create_view(self):
        response = self.client.post(reverse('cerfa_filler:companies-create'), {
            'label': 'New Company',
            'repository_code': '12345',
            'postal_code': '75003',
            'municipality': 'Lyon',
            'declarative_structure': self.declarative_structure.id,
            'cash_donation': 200.00,
            'inkind_donation': 100.00
        })
        print(response.content, response.headers)
        self.assertEqual(response.status_code, 200)  # Check for redirect
        self.assertTrue(Companies.objects.filter(label='New Company').exists())

    def test_companies_update_view(self):
        response = self.client.post(reverse('cerfa_filler:companies-update', args=[self.company.uuid]), {
            'label': 'Updated Company',
            'repository_code': '54321',
            'postal_code': '75002',
            'municipality': 'Paris',
            'declarative_structure': self.declarative_structure.id,
            'cash_donation': 150.00,
            'inkind_donation': 75.00
        })        # self.assertEqual(self.company.label, 'Updated Company')
        updated_company = Companies.objects.get(uuid=self.company.uuid) 
        self.company.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.company.label, 'Updated Company')
        self.assertEqual(updated_company.label, 'Updated Company')
        self.assertEqual(updated_company.total_donation, 225.00)

    def test_companies_cerfa_pdf_view(self):
        response = self.client.get(reverse('cerfa_filler:companies-cerfa-pdf', args=[self.company.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="recu_fiscal_don-', response['Content-Disposition'])

    def test_update_valid_date_view(self):
        response = self.client.post(reverse('cerfa_filler:update-valid-date'), {
            'selected_companies': [self.company.uuid]
        })
        self.company.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertIsNotNone(self.company.valid_date)  # Check if valid_date is updated
