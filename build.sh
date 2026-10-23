#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# ⚠️ TEMPORARY — delete after one successful deploy
python manage.py flush --no-input

# Ensure superuser exists AND has role=OWNER
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME}"
if not username:
    print("No DJANGO_SUPERUSER_USERNAME set, skipping")
else:
    u, created = User.objects.get_or_create(
        username=username,
        defaults={"email": "${DJANGO_SUPERUSER_EMAIL}"},
    )
    if created:
        u.set_password("${DJANGO_SUPERUSER_PASSWORD}")
        print(f"Created user {username}")
    if u.role != "OWNER" or not u.is_superuser:
        u.role = "OWNER"
        u.is_superuser = True
        u.is_staff = True
        u.save()
        print(f"Promoted {username} to OWNER + superuser")
    else:
        print(f"{username} is already OWNER + superuser")
EOF