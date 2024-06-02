"""
Mixins for managing authenticated access
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from players_app.models import Profile, GameCard


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
        user_profile = self.request.user.profile
        return user_profile.is_admin or str(self.profile_pk) == str(user_profile.pk)

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this profile.")
        return redirect(reverse_lazy('homepage'))


class GameCardOwnershipRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user_profile = self.request.user.profile
        try:
            gamecard = GameCard.objects.filter(pk=self.gamecard_pk).first()
            if gamecard:
                return user_profile.is_admin or gamecard in GameCard.objects.on_profile(profile=user_profile)
            else:
                messages.error(self.request, f"Gamecard was not found in our database.")
        except ValueError:
            messages.error(self.request, "Invalid gamecard ID.")
        return False

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this gamecard.")
        return redirect(reverse_lazy('homepage'))


class ProfileNotPrivateRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user_profile = self.request.user.profile
        try:
            profile = Profile.objects.filter(pk=self.profile_pk).first()
            if profile:
                return not profile.is_private or profile == user_profile or user_profile.is_admin
            else:
                messages.error(self.request, f"Profile was not found in our database.")
        except ValueError:
            messages.error(self.request, "Invalid profile ID.")
        return False

    def handle_no_permission(self):
        messages.error(self.request, "This profile is private.")
        return redirect(reverse_lazy('homepage'))


class GameCardNotPrivateRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user_profile = self.request.user.profile
        try:
            self.gamecard = GameCard.objects.filter(pk=self.gamecard_pk).first()
            if self.gamecard:
                return user_profile.is_admin or self.gamecard.profile == user_profile or not self.gamecard.profile.is_private
            else:
                messages.error(self.request, f"Gamecard was not found in our database.")
        except ValueError:
            messages.error(self.request, "Invalid gamecard ID.")
        return False

    def handle_no_permission(self):
        messages.error(self.request, "This gamecard is private.")
        return redirect(reverse_lazy('homepage'))
