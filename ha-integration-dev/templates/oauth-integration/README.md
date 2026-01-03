# OAuth2 Integration Template

Template for integrations that authenticate with cloud services using OAuth2.

## Features

- **OAuth2 Flow**: Standard authorization code flow
- **Application Credentials**: Secure client_id/secret storage
- **Token Refresh**: Automatic access token refresh
- **Reauth Support**: Handle expired/revoked tokens

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup, token management |
| `config_flow.py` | OAuth2 flow handler |
| `application_credentials.py` | OAuth2 provider configuration |
| `const.py` | OAuth URLs and scopes |
| `manifest.json` | Integration metadata |

## Customization Steps

### 1. Configure OAuth Endpoints

In `const.py`:
```python
OAUTH2_AUTHORIZE = "https://api.example.com/oauth/authorize"
OAUTH2_TOKEN = "https://api.example.com/oauth/token"
SCOPES = ["read", "write"]
```

### 2. Set Up Application Credentials

In `application_credentials.py`:
```python
class OAuth2Impl(AbstractOAuth2Implementation):
    @property
    def name(self) -> str:
        return "Example Service"

    @property
    def domain(self) -> str:
        return DOMAIN

    async def async_resolve_external_data(self, external_data):
        return external_data
```

### 3. Handle Token in API Calls

In your API client:
```python
class ExampleAPI:
    def __init__(self, token):
        self._token = token

    async def get_data(self):
        headers = {"Authorization": f"Bearer {self._token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, headers=headers) as resp:
                return await resp.json()
```

### 4. Add Token Refresh

In `__init__.py`:
```python
async def async_setup_entry(hass, entry):
    implementation = await async_get_config_entry_implementation(
        hass, entry
    )
    oauth_session = OAuth2Session(hass, entry, implementation)

    # Token is automatically refreshed
    token = await oauth_session.async_ensure_token_valid()
```

## OAuth2 Patterns

### Standard OAuth2 (Authorization Code)

Most common pattern for web services:
1. User clicks "Link Account"
2. Redirect to provider's authorize URL
3. User logs in and approves
4. Callback with authorization code
5. Exchange code for tokens

### PKCE (Proof Key for Code Exchange)

For mobile/native apps without client_secret:
```python
# Add to config_flow.py
code_verifier = secrets.token_urlsafe(32)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip("=")
```

### Reauth Flow

When tokens are revoked:
```python
async def async_step_reauth(self, entry_data):
    return await self.async_step_reauth_confirm()
```

## Registering with Provider

Most OAuth providers require app registration:
1. Create developer account
2. Register your application
3. Get client_id and client_secret
4. Configure redirect URI: `https://my.home-assistant.io/redirect/oauth`

## When to Use This Template

- Cloud services requiring user authorization
- Google, Microsoft, Spotify-style APIs
- Any service with "Login with X" buttons

## Resources

- [Home Assistant OAuth2 Documentation](https://developers.home-assistant.io/docs/config_entries_config_flow_handler#oauth2)
- [Application Credentials](https://developers.home-assistant.io/docs/config_entries_config_flow_handler#application-credentials)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
