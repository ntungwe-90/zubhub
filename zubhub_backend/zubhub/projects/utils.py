from django.conf import settings
from akismet import Akismet
from .models import Comment
from creators.tasks import send_mass_email, send_mass_text
from creators.models import Creator


def send_spam_notification(comment_id, staffs):
    email_contexts = []
    phone_contexts = []
    template_name = "spam_notification"
    for each in staffs:
        if each.email:
            email_contexts.append(
                {"user": each.username,
                 "email": each.email,
                 "comment_id": comment_id
                 }
            )

        if each.phone:
            phone_contexts.append(
                {
                    "phone": each.phone,
                    "comment_id": comment_id
                }
            )

    if len(email_contexts) > 0:
        send_mass_email.delay(
            template_name=template_name,
            ctxs=email_contexts
        )

    if len(phone_contexts) > 0:
        send_mass_text.delay(
            template_name=template_name,
            ctxs=phone_contexts
        )


def filter_spam(ctx):

    site_url = settings.DEFAULT_BACKEND_PROTOCOL + \
        "://"+settings.DEFAULT_BACKEND_DOMAIN

    if site_url.find("localhost") != -1:
        return

    comment = Comment.objects.get(id=ctx.get("comment_id"))

    if ctx.get("method") == 'POST' and comment.published:
        akismet_api = Akismet(key=settings.AKISMET_API_KEY,
                              blog_url=site_url)

        is_spam = akismet_api.comment_check(
            user_ip=ctx.get("REMOTE_ADDR"),
            user_agent=ctx.get("HTTP_USER_AGENT"),
            comment_type='comment',
            comment_content=ctx.get("text"),
            blog_lang=ctx.get("lang"),
        )

        if is_spam:
            comment.published = False
            comment.save()

            staffs = Creator.objects.filter(is_staff=True)

            send_spam_notification(ctx.get("comment_id"), staffs)