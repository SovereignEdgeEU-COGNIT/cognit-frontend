from biscuit_auth import Authorizer, Biscuit, BiscuitValidationError, BiscuitBuilder, KeyPair
from datetime import datetime, timedelta, timezone
import pyone

keypair = KeyPair()
ONE_XMLRPC = None  # Set when importing module


def authenticate(user: str, password: str) -> bool:
    one = pyone.OneServer(ONE_XMLRPC, session="{user}:{password}")

    try:
        one.userpool.info()
        return True
    except pyone.OneAuthenticationException as e:
        return False


def generate_biscuit(user: str, private_key=keypair.private_key) -> str:

    token = BiscuitBuilder("""
    user({user_id});
    check if time($time), $time < {expiration};
    """,
                           {
                               'user_id': user,
                               'expiration': datetime.now(tz=timezone.utc) + timedelta(days=1)
                           }
                           ).build(private_key)
    return token.to_base64()


def authorize_biscuit(token64: str, public_key=keypair.public_key):
    try:
        token = Biscuit.from_base64(token64, public_key)
    except BiscuitValidationError as e:
        return e

    authorizer = Authorizer(""" time({now}); allow if user($u); """, {
                            'now': datetime.now(tz=timezone.utc)})
    authorizer.add_token(token)
    authorizer.authorize()
