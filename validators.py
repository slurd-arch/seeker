import re
import ipaddress

try:
    import phonenumbers
    PHONE_OK = True
except ImportError:
    PHONE_OK = False

try:
    from email_validator import validate_email, EmailNotValidError
    EMAIL_OK = True
except ImportError:
    EMAIL_OK = False


def validate_email_input(email):
    if not EMAIL_OK:
        # Fallback regex
        pat = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        return (True, email) if re.match(pat, email) else (False, "Invalid email")
    try:
        v = validate_email(email, check_deliverability=False)
        return True, v.normalized
    except EmailNotValidError as e:
        return False, str(e)


def validate_ip_input(ip):
    try:
        ipaddress.ip_address(ip)
        return True, ip
    except ValueError:
        return validate_domain_input(ip)


def validate_phone_input(phone):
    if not PHONE_OK:
        return (True, phone) if phone else (False, "Empty phone")
    try:
        p = phonenumbers.parse(phone, None)
        if phonenumbers.is_valid_number(p):
            return True, phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
        return False, "Invalid phone number"
    except Exception as e:
        return False, str(e)


def validate_username_input(username):
    if not username or len(username) < 2 or len(username) > 50:
        return False, "Username must be 2-50 characters"
    if not re.match(r'^[a-zA-Z0-9._\-]+$', username):
        return False, "Username contains invalid characters"
    return True, username


def validate_domain_input(domain):
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if re.match(pattern, domain):
        return True, domain.lower()
    return False, "Invalid domain format"


def validate(query, query_type):
    validators = {
        "email": validate_email_input,
        "ip": validate_ip_input,
        "phone": validate_phone_input,
        "username": validate_username_input,
        "domain": validate_domain_input,
    }
    fn = validators.get(query_type, lambda x: (True, x))
    return fn(query)