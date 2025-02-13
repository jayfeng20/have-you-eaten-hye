from jose import jwt, jwk
import httpx
from dotenv import load_dotenv
import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json

load_dotenv()

# Cognito user pool details
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
REGION = os.getenv("REGION")
AUDIENCE = os.getenv("COGNITO_APP_CLIENT_ID")
ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_signing_key(token: str) -> dict:
    """
    Retrieve the signing key from the JWKS endpoint that matches the token's 'kid' header.
    This version uses httpx for asynchronous HTTP requests.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        raise ValueError(f"Unable to get token header: {e}")

    kid = unverified_header.get("kid")
    if not kid:
        raise ValueError("Token header does not contain 'kid'")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(JWKS_URL)
        logger.info(f"JWKS response status: {response.status_code}")
        response.raise_for_status()
        jwks = response.json()

    # jwks = json.loads('{"keys":[{"alg":"RS256","e":"AQAB","kid":"ihVFLINL28qLxnNG1faQUo+izQMBOLPfF9lcRT6QQV4=","kty":"RSA","n":"vxJDz_WZ5nkKq5_TiYzPKKB7tCXxKWZAYq9LuFjpssxVcn50GutREuKCX8IdKNVEORDXqByto2_-5Htg3nFDXPgVofrGD3ybcLSmGr-MVWGk42Lc2EdtZmdw7PM1Te21JAcF2wOgrhkuxLSq88KYRrG5-GABOdB993SexqFDKuQfZPXw7L66cLrMYPco7t_CUUb2HE1N8DKw3iW-w7QI2Q_gC7k_aJwI7QOW7Fnckbz9ZkVCt0zliez5OyUk2tCgNxSNfcrzfyttZLEhvhZPDroseDVfajONthS3U-pVqEqnl7szspmD27gk4-I8NbEdcwKtv3Ci__KuDxm1Zi08aw","use":"sig"},{"alg":"RS256","e":"AQAB","kid":"3XB+SrIHLVUqVpVLfSEjjiHzG3rCoOfEdmL0u/SjNAg=","kty":"RSA","n":"4jgoOsSsygdpRPn3HJ9Lwr5Mg7T1LEKUF9ghTAOTa_mJfaY7oqpzY_4uef0Q3b1virZkuhk5leUcI-kEqM_vlJLONNU-NFTeqLu2VZb9T7TeO8iJhNam1FvgDRmKmTmlGZ7J3tYgQpj5o_9VqbfnRHVeBI2jX3CxNdgqGMvEUH9Psqvh75ROhE1TEUsMQI--tQR6a5o3niejMoQgjUb3FuN0M07FvvZcV1Q_LUjLMMf-ZFhujVqACZnhojpIfSICuaRVDrO2u9TF9alFWla5rQRkGvbJS7UYm6VGxCKFod4oUN1XFFuyNmZJWGT45uGV0Hf9QPIrjmQx6SGpKt_LHQ","use":"sig"}]}')

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise ValueError("Unable to find the appropriate key for token verification")


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify the token using the public key from JWKS and return the payload if verification is successful.
    """
    try:
        token = credentials.credentials
        logger.info(
            f"Verifying token: {token[:30]}..."
        )  # log a truncated token for security
        signing_key = await get_signing_key(token)
        logger.info(f"Acquired signing key")

        # Convert the JWK dict to a PEM-encoded RSA public key using jwk.construct
        pem_key = jwk.construct(signing_key, algorithm="RS256").to_pem().decode("utf-8")
        logger.info("Converted signing key to PEM format.")

        # Decode and verify the token using the PEM key
        payload = jwt.decode(
            token,
            pem_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )

        logger.info("Token verification successful.")
        return payload
    except Exception as e:
        logger.error(f"Token verification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}",
        )
