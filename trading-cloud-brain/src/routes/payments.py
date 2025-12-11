"""
💳 PAYMENTS ROUTE HANDLER
Handles checkout sessions for Stripe, PayPal, and Coinbase.
"""

from js import Response, fetch, Headers, JSON
import json
from base64 import b64encode

# Pricing Configuration
TIERS = {
    "Adept": {"price": 2900, "currency": "usd", "name": "Adept Plan"},        # $29.00
    "Grandmaster": {"price": 9900, "currency": "usd", "name": "Grandmaster Plan"} # $99.00
}

async def handle_checkout(request, env, headers):
    """
    Handle payment checkout request.
    Expected JSON: { "tier": "Adept", "provider": "Stripe" }
    """
    if request.method != "POST":
        return Response.new(json.dumps({"error": "Method not allowed"}), status=405, headers=headers)

    try:
        body_js = await request.json()
        body = json.loads(JSON.stringify(body_js))

        tier = body.get("tier")
        provider = body.get("provider")

        if not tier or not provider:
             return Response.new(json.dumps({"error": "Missing tier or provider"}), status=400, headers=headers)

        if tier not in TIERS:
            return Response.new(json.dumps({"error": "Invalid tier"}), status=400, headers=headers)

        # Determine base URL for callbacks
        # Use environment variable if set, otherwise derive from request
        base_url = str(getattr(env, 'APP_BASE_URL', ''))
        if not base_url:
            # Derive from request url (e.g., https://worker.dev/api/...)
            url_str = str(request.url)
            if "://" in url_str:
                base_url = "/".join(url_str.split("/")[:3])
            else:
                # Fallback
                base_url = "https://trading-brain-v1.amrikyy.workers.dev"

        # Dispatch to provider
        if provider == "Stripe":
            return await create_stripe_session(tier, env, headers, base_url)
        elif provider == "PayPal":
             return await create_paypal_order(tier, env, headers, base_url)
        elif provider == "Coinbase":
             return await create_coinbase_charge(tier, env, headers, base_url)
        else:
             return Response.new(json.dumps({"error": "Invalid provider"}), status=400, headers=headers)

    except Exception as e:
         return Response.new(json.dumps({"error": str(e)}), status=500, headers=headers)


async def create_stripe_session(tier, env, headers, base_url):
    """Create Stripe Checkout Session"""
    stripe_key = str(getattr(env, 'STRIPE_SECRET_KEY', ''))

    if not stripe_key:
        return mock_checkout_response(tier, "Stripe", headers, base_url)

    price_data = TIERS[tier]

    try:
        # Form URL Encoded Body
        params = {
            "payment_method_types[0]": "card",
            "line_items[0][price_data][currency]": price_data["currency"],
            "line_items[0][price_data][product_data][name]": price_data["name"],
            "line_items[0][price_data][unit_amount]": str(price_data["price"]),
            "line_items[0][quantity]": "1",
            "mode": "subscription",
            "success_url": f"{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{base_url}/payment/cancel",
        }

        body_parts = []
        for key, value in params.items():
            body_parts.append(f"{key}={value}")
        body_str = "&".join(body_parts)

        req_headers = Headers.new({
            "Authorization": f"Bearer {stripe_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }.items())

        response = await fetch("https://api.stripe.com/v1/checkout/sessions",
            method="POST", headers=req_headers, body=body_str)

        data = json.loads(await response.text())

        if response.ok:
            return Response.new(json.dumps({"checkoutUrl": data["url"]}), headers=headers)
        else:
            return Response.new(json.dumps({"error": data.get("error", {}).get("message", "Stripe Error")}), status=400, headers=headers)

    except Exception as e:
        return Response.new(json.dumps({"error": str(e)}), status=500, headers=headers)


async def create_paypal_order(tier, env, headers, base_url):
    """Create PayPal Order"""
    client_id = str(getattr(env, 'PAYPAL_CLIENT_ID', ''))
    secret = str(getattr(env, 'PAYPAL_SECRET', ''))

    if not client_id or not secret:
        return mock_checkout_response(tier, "PayPal", headers, base_url)

    price_data = TIERS[tier]
    amount = price_data["price"] / 100 # Convert cents to dollars

    try:
        # 1. Get Access Token
        auth_str = f"{client_id}:{secret}"
        auth_b64 = b64encode(auth_str.encode('utf-8')).decode('utf-8')

        token_headers = Headers.new({
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }.items())

        token_res = await fetch("https://api-m.paypal.com/v1/oauth2/token",
            method="POST", headers=token_headers, body="grant_type=client_credentials")

        token_data = json.loads(await token_res.text())
        access_token = token_data.get("access_token")

        if not access_token:
             return Response.new(json.dumps({"error": "PayPal Auth Failed"}), status=500, headers=headers)

        # 2. Create Order
        order_payload = json.dumps({
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "USD",
                    "value": f"{amount:.2f}"
                },
                "description": price_data["name"]
            }],
            "application_context": {
                "return_url": f"{base_url}/payment/success",
                "cancel_url": f"{base_url}/payment/cancel"
            }
        })

        order_headers = Headers.new({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }.items())

        order_res = await fetch("https://api-m.paypal.com/v2/checkout/orders",
            method="POST", headers=order_headers, body=order_payload)

        order_data = json.loads(await order_res.text())

        # Find approval link
        approve_link = next((link["href"] for link in order_data.get("links", []) if link["rel"] == "approve"), None)

        if approve_link:
             return Response.new(json.dumps({"checkoutUrl": approve_link}), headers=headers)
        else:
             return Response.new(json.dumps({"error": "PayPal Order Creation Failed"}), status=500, headers=headers)

    except Exception as e:
         return Response.new(json.dumps({"error": str(e)}), status=500, headers=headers)


async def create_coinbase_charge(tier, env, headers, base_url):
    """Create Coinbase Commerce Charge"""
    api_key = str(getattr(env, 'COINBASE_COMMERCE_API_KEY', ''))

    if not api_key:
        return mock_checkout_response(tier, "Coinbase", headers, base_url)

    price_data = TIERS[tier]
    amount = price_data["price"] / 100

    try:
        payload = json.dumps({
            "name": price_data["name"],
            "description": f"Subscription to {tier}",
            "pricing_type": "fixed_price",
            "local_price": {
                "amount": f"{amount:.2f}",
                "currency": "USD"
            },
            "metadata": {
                "customer_id": "user_123", # TODO: Get from request context
                "tier": tier
            },
            "redirect_url": f"{base_url}/payment/success",
            "cancel_url": f"{base_url}/payment/cancel"
        })

        req_headers = Headers.new({
            "X-CC-Api-Key": api_key,
            "X-CC-Version": "2018-03-22",
            "Content-Type": "application/json"
        }.items())

        response = await fetch("https://api.commerce.coinbase.com/charges",
            method="POST", headers=req_headers, body=payload)

        data = json.loads(await response.text())

        hosted_url = data.get("data", {}).get("hosted_url")

        if hosted_url:
             return Response.new(json.dumps({"checkoutUrl": hosted_url}), headers=headers)
        else:
             return Response.new(json.dumps({"error": "Coinbase Charge Failed"}), status=500, headers=headers)

    except Exception as e:
        return Response.new(json.dumps({"error": str(e)}), status=500, headers=headers)


def mock_checkout_response(tier, provider, headers, base_url):
    """Return a mock checkout URL for testing/demo"""
    return Response.new(json.dumps({
        "checkoutUrl": f"{base_url}/payment/mock-success?tier={tier}&provider={provider}",
        "message": "Simulated Checkout (Missing API Keys)"
    }), headers=headers)
