import hashlib
import hmac

from django.conf import settings


def get_at(index, t):
    try:
        value = t[index]
    except IndexError:
        value = None
    return value


def get_s3direct_destinations():
    """Returns s3direct destinations.

    NOTE: Don't use constant as it will break ability to change at runtime (e.g. tests)
    """
    return getattr(settings, 'S3DIRECT_DESTINATIONS', None)


# AWS Signature v4 Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python

def sign(key, message):
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def get_access_key():
    return getattr(settings, 'S3_DIRECT_ACCESS_KEY_ID', None) or getattr(settings, 'AWS_ACCESS_KEY_ID', None)


def get_signing_secret_key():
    return getattr(settings, 'S3_DIRECT_SECRET_ACCESS_KEY', None) or settings.AWS_SECRET_ACCESS_KEY


def get_aws_v4_signing_key(key, signing_date, region, service):
    datestamp = signing_date.strftime('%Y%m%d')
    date_key = sign(('AWS4' + key).encode('utf-8'), datestamp)
    k_region = sign(date_key, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing


def get_aws_v4_signature(key, message):
    return hmac.new(key, message.encode('utf-8'), hashlib.sha256).hexdigest()


def get_key(key, file_name, dest):
    if hasattr(key, '__call__'):
        fn_args = [file_name, ]
        args = dest.get('key_args')
        if args:
            fn_args.append(args)
        object_key = key(*fn_args)
    elif key == '/':
        object_key = file_name
    else:
        object_key = '%s/%s' % (key.strip('/'), file_name)
    return object_key
