from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

class OwnerListView(ListView):
    """
    Sub-class the ListView to pass the request to the form.
    """

class OwnerDetailView(DetailView):
    """
    Sub-class the DetailView to pass the request to the form.
    """

class OwnerCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        print('form valid called')
        object = form.save(commit = False)
        object.owner = self.request.user
        object.save()
        return super(OwnerCreateView, self).form_valid(form)

class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        print('update get_queryset called')
        qs = super(OwnerUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        print('delete get_queryset called')
        qs = super(OwnerDeleteView, self).get_queryset()
        return qs.filter(user=self.request.user)
