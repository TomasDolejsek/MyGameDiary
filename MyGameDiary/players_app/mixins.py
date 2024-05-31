"""
Mixins for managing authenticated access
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from players_app.models import Profile


class UserRightsMixin:
    allowed_groups = []

    @staticmethod
    def is_member_of(user, group_names):
        if 'All' in group_names:
            return True
        return user.groups.filter(name__in=group_names).exists()

    def get_context_rights(self, *args, **kwargs):
        context = {'user_has_rights': self.is_member_of(self.request.user, self.allowed_groups)}
        return context


class AnonymousRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        messages.error(self.request, "You are already logged in.")
        return redirect(reverse_lazy('homepage'))


class ProfileOwnershipRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        profile_pk = self.request.GET.get('profile_pk')
        user_profile = self.request.user.profile
        return user_profile.is_admin or str(profile_pk) == str(user_profile.pk)

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this profile.")
        return redirect(reverse_lazy('homepage'))


class ProfileNotPrivateRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        profile_pk = self.request.GET.get('profile_pk')
        user_profile = self.request.user.profile
        try:
            profile = Profile.objects.filter(pk=profile_pk).first()
            if profile:
                return user_profile.is_admin or profile == user_profile or not profile.is_private
            else:
                messages.error(self.request, f"Profile with id {profile_pk} was not found in our database.")
        except ValueError:
            messages.error(self.request, f"'{profile_pk}' is not a valid profile id.")
        return False

    def handle_no_permission(self):
        messages.error(self.request, "This profile is private.")
        return redirect(reverse_lazy('homepage'))
    