from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

# Create a reusable HTTPBearer instance
security = HTTPBearer()

# These values should be configured for your environment.
# For Cognito, you can fetch the JWKS and use the appropriate public key.
PUBLIC_KEY = "YOUR_COGNITO_PUBLIC_KEY"  # Replace with your actual public key
ALGORITHM = "RS256"
AUDIENCE = "YOUR_API_AUDIENCE"  # e.g., your app client ID


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Decode and verify the token.
        # This will raise a JWTError if verification fails.
        payload = jwt.decode(
            token, PUBLIC_KEY, algorithms=[ALGORITHM], audience=AUDIENCE
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from e

    # Optionally, you can return specific claims from the payload.
    return payload
