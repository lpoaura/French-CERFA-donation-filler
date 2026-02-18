from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView

User = get_user_model()


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "delete_account.html"
    success_url = reverse_lazy("home")

    def get_object(self):
        # Empêche de supprimer un autre utilisateur
        return self.request.user

    def form_valid(self, form):
        # Déconnecte l'utilisateur avant suppression
        logout(self.request)
        return super().form_valid(form)
