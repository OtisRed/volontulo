# -*- coding: utf-8 -*-

u"""
.. module:: offers
"""

from django.contrib.admin.models import ADDITION
from django.contrib.admin.models import CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import View

from volontulo.forms import CreateOfferForm
from volontulo.forms import OfferApplyForm
from volontulo.lib.email import send_mail
from volontulo.models import Badge
from volontulo.models import Offer
from volontulo.models import UserBadges
from volontulo.models import UserProfile
from volontulo.utils import OFFERS_STATUSES
from volontulo.utils import save_history
from volontulo.utils import yield_message_error
from volontulo.utils import yield_message_successful
from volontulo.views import logged_as_admin


def offers_list(request):
    u"""View, that show list of offers.

    It's used for volunteers to show active ones and for admins to show
    all of them.
    """
    if logged_as_admin(request):
        offers = Offer.objects.all()
    else:
        offers = Offer.objects.filter(status='ACTIVE')
    return render(request, "offers/offers_list.html", context={
        'offers': offers,
    })


class OffersCreate(View):
    u"""Class view supporting creation of new offer."""

    @staticmethod
    def get(request):
        u"""Method responsible for rendering form for new offer."""
        user = UserProfile.objects.get(user=request.user)
        organization = user.organization

        form = CreateOfferForm()
        context = {
            'offer_form': form,
            'organization': organization,
            'statuses': OFFERS_STATUSES,
            'user': user,
            'offer': Offer(),
        }

        return render(
            request,
            'offers/offer_form.html',
            context
        )

    @staticmethod
    def post(request):
        u"""Method resposible for saving new offer."""
        user = UserProfile.objects.get(user=request.user)
        organization = user.organization
        form = CreateOfferForm(request.POST)

        if form.is_valid():
            offer = form.save()
            save_history(request, offer, action=ADDITION)
            ctx = {
                'domain': request.build_absolute_uri().replace(
                    request.get_full_path(),
                    ''
                ),
                'address_sufix': reverse(
                    'offers_view',
                    args=[organization.id, offer.id]
                ),
                'offer': offer
            }
            send_mail(
                'offer_creation',
                ['administrators@volontuloapp.org'],
                ctx
            )
            yield_message_successful(
                request,
                u"Dziękujemy za dodanie oferty."
            )
            return redirect(
                reverse(
                    'offers_view',
                    args=[organization.id, offer.id]
                ),
            )
        yield_message_error(
            request,
            u"Formularz zawiera niepoprawnie wypełnione pola"
        )
        return render(
            request,
            'offers/offer_form.html',
            {
                'offer_form': form,
                'organization': organization,
                'statuses': OFFERS_STATUSES,
                'user': user,
                'offer': Offer()
            }
        )


class OffersEdit(View):
    u"""Class view supporting change of a offer."""

    @staticmethod
    def get(request, slug, offer_id):  # pylint: disable=unused-argument
        u"""Method responsible for rendering form for offer to be changed."""
        offer = Offer.objects.get(pk=offer_id)
        organization = offer.organization
        user = UserProfile.objects.get(user=request.user)
        form = CreateOfferForm()

        context = {
            'offer_form': form,
            'organization': organization,
            'statuses': OFFERS_STATUSES,
            'user': user,
            'offer': offer,
        }

        return render(
            request,
            'offers/offer_form.html',
            context
        )

    @staticmethod
    def post(request, slug, offer_id):  # pylint: disable=unused-argument
        u"""Method resposible for saving changed offer."""
        offer = Offer.objects.get(pk=offer_id)

        if request.POST['edit_type'] == 'status_change':
            offer.status = request.POST['status']
            offer.save()
            return redirect('offers_list')

        organization = offer.organization
        user = UserProfile.objects.get(user=request.user)
        form = CreateOfferForm(request.POST, instance=offer)

        if form.is_valid():
            offer = form.save()
            save_history(request, offer, action=CHANGE)
            yield_message_successful(
                request,
                u"Oferta została zmieniona."
            )
            if offer_id:
                yield_message_successful(
                    request,
                    u"Oferta została zmieniona."
                )
            else:
                ctx = {
                    'domain': request.build_absolute_uri().replace(
                        request.get_full_path(),
                        ''
                    ),
                    'address_sufix': reverse(
                        'show_offer',
                        args=[organization.id, offer.id]
                    ),
                    'offer': offer
                }
                send_mail(
                    'offer_creation',
                    ['administrators@volontuloapp.org'],
                    ctx
                )
                yield_message_successful(
                    request,
                    u"Dziękujemy za dodanie oferty."
                )
                return redirect(
                    reverse(
                        'show_offer',
                        args=[organization.id, offer.id]
                    ),
                )
        else:
            yield_message_error(
                request,
                u"Formularz zawiera niepoprawnie wypełnione pola"
            )
        return render(
            request,
            'offers/offer_form.html',
            {
                'offer_form': form,
                'organization': organization,
                'statuses': OFFERS_STATUSES,
                'user': user,
                'offer': Offer()
            }
        )


def offers_view(request, slug, offer_id):  # pylint: disable=unused-argument
    u"""View responsible for showing details of particular offer."""
    offer = get_object_or_404(Offer, id=offer_id)
    context = {
        'offer': offer,
    }
    user = UserProfile.objects.filter(user__id=request.user.id)[0]
    if user.is_administrator:
        context['user'] = user
        context['volunteers'] = offer.volunteers.all()
    return render(request, "offers/show_offer.html", context=context)


def offers_join(request, slug, offer_id):  # pylint: disable=unused-argument
    u"""Handling volounteer applying for helping with offer."""
    if not request.user:
        return redirect('login')

    volunteer_user = UserProfile.objects.get(user=request.user)
    offer_content_type = ContentType.objects.get(
        app_label='volontulo',
        model='offer'
    )
    has_applied = Offer.objects.filter(
        volunteers__id=request.user.id,
        volunteers__offer=offer_id,
    ).count()
    if has_applied:
        yield_message_error(
            request,
            u'Już wyraziłeś chęć uczestnictwa w tej ofercie.'
        )
        return redirect('offers_list')

    offer = Offer.objects.get(pk=offer_id)

    if request.method == 'POST':
        form = OfferApplyForm(request.POST)

        if form.is_valid():
            offer.volunteers.add(request.user)
            apply_participant_badge(offer_content_type, volunteer_user)
            offer.save()

            domain = request.build_absolute_uri().replace(
                request.get_full_path(),
                ''
            )
            send_mail(
                'offer_application',
                [
                    request.user.user.email,
                    request.POST.get('email'),
                ],
                dict(
                    email=request.POST.get('email'),
                    phone_no=request.POST.get('phone_no'),
                    fullname=request.POST.get('fullname'),
                    comments=request.POST.get('comments'),
                    offer_url=domain + reverse(
                        'offers_view',
                        args=[slugify(offer.title), offer_id]),
                    offer_id=offer_id
                )
            )
            yield_message_successful(
                request,
                u'Zgłoszenie chęci uczestnictwa zostało wysłane.'
            )
            return redirect(
                reverse(
                    'offers_view',
                    args=[slugify(offer.title), offer_id]
                ),
            )
        else:
            errors = '<br />'.join(form.errors)
            yield_message_error(
                request,
                u'Formularz zawiera nieprawidłowe dane' + errors
            )
    else:
        form = OfferApplyForm()

    context = {
        'form': form,
        'offer': offer,
    }
    if not (
            volunteer_user.is_administrator and
            volunteer_user.is_organization
    ):
        context['volunteer_user'] = volunteer_user

    return render(
        request,
        'offers/offer_apply.html',
        context
    )


def apply_participant_badge(offer_content_type, volunteer_user):
    u"""Helper function to apply particpant badge to specified user."""
    badge = Badge.objects.get(slug='participant')
    user_badges = UserBadges.objects.create(
        userprofile=volunteer_user,
        badge=badge,
        content_type=offer_content_type,
        created_at=timezone.now(),
        description=u"Wolontariusz {} zgłosił chęć pomocy.".format(
            volunteer_user.user.email
        )
    )
    return user_badges.save()
