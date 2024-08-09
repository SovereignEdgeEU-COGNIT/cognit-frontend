from biscuit_auth import Authorizer, Biscuit, BiscuitBuilder, BlockBuilder, KeyPair, PrivateKey, PublicKey, Rule, UnverifiedBiscuit
from datetime import datetime, timedelta, timezone
import pyone

keypair = KeyPair()
ONE_XMLRPC = None

def authenticate(user: str, password: str):
    one = pyone.OneServer(ONE_XMLRPC, session="{user}:{password}")

    try:
        one.userpool.info()
        return True
    except pyone.OneAuthenticationException as e:
        return False

def generate_biscuit(user: str) -> str:

    token = BiscuitBuilder("""
    user({user_id});
    check if time($time), $time < {expiration};
    """,
    {
        'user_id': user,
        'expiration': datetime.now(tz=timezone.utc) + timedelta(days = 1)
    }
    ).build(keypair.private_key)
    return token.to_base64()

def authorize_biscuit(token64: str) -> int:
    token = Biscuit.from_base64(token64, keypair.public_key)
    authorizer = Authorizer(""" time({now}); allow if user($u); """, {
                            'now': datetime.now(tz=timezone.utc)})

    authorizer.add_token(token)
    authorizer.authorize()
