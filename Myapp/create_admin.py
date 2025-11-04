from django.contrib.auth import get_user_model

User = get_user_model()

username = "Admin"
password = "123"
email = "admin@example.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superuser created successfully!")
else:
    print("⚠️ Superuser already exists.")
