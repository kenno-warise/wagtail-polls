from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-q2-4-ftjoe&53p1=%!jt9f6-0v3&2z9y0f0kb)%x(7=1c$*+c#"

# SECURITY WARNING: define the correct hosts in production!
# ALLOWED_HOSTS = ["*"]
# unittestではDEBUG=Falseになりアスタリスク（*）では無効なHTTP_HOSTヘッダーとみなされるので設定
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
