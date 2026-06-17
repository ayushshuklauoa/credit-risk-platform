from fastapi import APIRouter, HTTPException, Depends, Request, Response
import httpx
from app.config import SERVICE_REGISTRY
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# HTTP client for service-to-service communication
async def get_http_client():
    """Async HTTP client factory"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


def forward_response(response: httpx.Response) -> Response:
    """Return upstream response without hiding its HTTP status code."""
    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json")
    )

# Auth Service Routes
@router.post("/auth/register", tags=["Auth"])
async def register(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Forward registration request to Auth Service"""
    body = await request.json()

    auth_url = f"{SERVICE_REGISTRY['auth']}/auth/register"
    try:
        response = await client.post(auth_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Auth Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Auth Service unavailable")


@router.post("/auth/login", tags=["Auth"])
async def login(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Forward login request to Auth Service"""
    body = await request.json()
    
    auth_url = f"{SERVICE_REGISTRY['auth']}/auth/login"
    try:
        response = await client.post(auth_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Auth Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Auth Service unavailable")

@router.post("/auth/refresh", tags=["Auth"])
async def refresh_token(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Forward token refresh to Auth Service"""
    body = await request.json()
    
    auth_url = f"{SERVICE_REGISTRY['auth']}/auth/refresh"
    try:
        response = await client.post(auth_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Auth Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Auth Service unavailable")

# Customer Service Routes
@router.get("/customers/{customer_id}", tags=["Customer"])
async def get_customer(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get customer by ID"""
    customer_url = f"{SERVICE_REGISTRY['customer']}/customers/{customer_id}"
    try:
        response = await client.get(customer_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Customer Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Customer Service unavailable")

@router.post("/customers", tags=["Customer"])
async def create_customer(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Create new customer"""
    body = await request.json()
    
    customer_url = f"{SERVICE_REGISTRY['customer']}/customers"
    try:
        response = await client.post(customer_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Customer Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Customer Service unavailable")

# Account Service Routes
@router.get("/accounts/{account_id}", tags=["Account"])
async def get_account(account_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get account by ID"""
    account_url = f"{SERVICE_REGISTRY['account']}/accounts/{account_id}"
    try:
        response = await client.get(account_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

@router.post("/accounts", tags=["Account"])
async def create_account(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Create new account"""
    body = await request.json()
    
    account_url = f"{SERVICE_REGISTRY['account']}/accounts"
    try:
        response = await client.post(account_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

@router.get("/accounts/{account_id}/transactions", tags=["Account"])
async def get_transactions(account_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get account transactions"""
    tx_url = f"{SERVICE_REGISTRY['account']}/accounts/{account_id}/transactions"
    try:
        response = await client.get(tx_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

# Credit Scoring Routes
@router.get("/credit/summary/{customer_id}", tags=["Credit"])
async def get_credit_summary(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get credit summary for customer"""
    credit_url = f"{SERVICE_REGISTRY['credit']}/credit/summary/{customer_id}"
    try:
        response = await client.get(credit_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Credit Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Credit Service unavailable")

# Fraud Detection Routes
@router.post("/fraud/alerts", tags=["Fraud"])
async def create_fraud_alert(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Create fraud alert"""
    body = await request.json()
    
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/alerts"
    try:
        response = await client.post(fraud_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

@router.get("/fraud/customers/{customer_id}/alerts", tags=["Fraud"])
async def get_fraud_alerts(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get fraud alerts for customer"""
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/alerts"
    try:
        response = await client.get(fraud_url, params={"customer_id": customer_id})
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

# Document AI Routes
@router.post("/documents/upload", tags=["Document"])
async def upload_document(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Upload and process document"""
    doc_url = f"{SERVICE_REGISTRY['document']}/api/documents/documents/upload"
    try:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            data = {}
            files = {}
            for key, value in form.multi_items():
                if hasattr(value, "filename"):
                    files[key] = (
                        value.filename,
                        await value.read(),
                        value.content_type or "application/octet-stream"
                    )
                else:
                    data[key] = str(value)

            response = await client.post(
                doc_url,
                params=dict(request.query_params),
                data=data,
                files=files
            )
        else:
            body = await request.json()
            response = await client.post(doc_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Document Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Document Service unavailable")

@router.get("/documents/{document_id}", tags=["Document"])
async def get_document(document_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get document by ID"""
    doc_url = f"{SERVICE_REGISTRY['document']}/api/documents/documents/{document_id}"
    try:
        response = await client.get(doc_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Document Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Document Service unavailable")

# Credit Scoring Advanced Routes
@router.post("/credit/calculate-score", tags=["Credit"])
async def calculate_credit_score(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Calculate credit score"""
    body = await request.json()
    
    credit_url = f"{SERVICE_REGISTRY['credit']}/credit/calculate-score"
    try:
        response = await client.post(credit_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Credit Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Credit Service unavailable")

@router.post("/credit/assess-risk", tags=["Credit"])
async def assess_risk(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Assess customer risk profile"""
    body = await request.json()
    
    credit_url = f"{SERVICE_REGISTRY['credit']}/credit/assess-risk"
    try:
        response = await client.post(credit_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Credit Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Credit Service unavailable")

@router.get("/credit/score/{customer_id}", tags=["Credit"])
async def get_credit_score(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get credit score for customer"""
    credit_url = f"{SERVICE_REGISTRY['credit']}/credit/score/{customer_id}"
    try:
        response = await client.get(credit_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Credit Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Credit Service unavailable")

@router.get("/credit/risk/{customer_id}", tags=["Credit"])
async def get_risk_profile(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get risk profile for customer"""
    credit_url = f"{SERVICE_REGISTRY['credit']}/credit/risk/{customer_id}"
    try:
        response = await client.get(credit_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Credit Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Credit Service unavailable")

@router.post("/credit/generate-report", tags=["Credit"])
async def generate_credit_report(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Generate credit report"""
    body = await request.json()
    
    credit_url = f"{SERVICE_REGISTRY['credit']}/credit/generate-report"
    try:
        response = await client.post(credit_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Credit Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Credit Service unavailable")

@router.get("/credit/report/{customer_id}", tags=["Credit"])
async def get_credit_report(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get latest credit report for customer"""
    credit_url = f"{SERVICE_REGISTRY['credit']}/credit/report/{customer_id}"
    try:
        response = await client.get(credit_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Credit Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Credit Service unavailable")

# Account Service Advanced Routes
@router.post("/accounts/{account_id}/deposit", tags=["Account"])
async def deposit(account_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Deposit to account"""
    body = await request.json()
    
    account_url = f"{SERVICE_REGISTRY['account']}/accounts/{account_id}/deposit"
    try:
        response = await client.post(account_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

@router.post("/accounts/{account_id}/withdraw", tags=["Account"])
async def withdraw(account_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Withdraw from account"""
    body = await request.json()
    
    account_url = f"{SERVICE_REGISTRY['account']}/accounts/{account_id}/withdraw"
    try:
        response = await client.post(account_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

@router.post("/accounts/transfer", tags=["Account"])
async def transfer_money(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Transfer money between accounts"""
    body = await request.json()
    
    account_url = f"{SERVICE_REGISTRY['account']}/accounts/transfer"
    try:
        response = await client.post(account_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

@router.get("/accounts/{account_id}/balance", tags=["Account"])
async def get_balance(account_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get account balance"""
    account_url = f"{SERVICE_REGISTRY['account']}/accounts/{account_id}/balance"
    try:
        response = await client.get(account_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

@router.get("/accounts/{account_id}/statement", tags=["Account"])
async def get_statement(account_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get account statement"""
    account_url = f"{SERVICE_REGISTRY['account']}/accounts/{account_id}/statement"
    try:
        response = await client.get(account_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Account Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Account Service unavailable")

# Fraud Detection Advanced Routes
@router.post("/fraud/assess-risk", tags=["Fraud"])
async def assess_fraud_risk(request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Assess fraud risk"""
    body = await request.json()
    
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/assess-risk"
    try:
        response = await client.post(fraud_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

@router.get("/fraud/alerts/{alert_id}", tags=["Fraud"])
async def get_fraud_alert_detail(alert_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get fraud alert details"""
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/alerts/{alert_id}"
    try:
        response = await client.get(fraud_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

@router.put("/fraud/alerts/{alert_id}", tags=["Fraud"])
async def update_fraud_alert(alert_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Update fraud alert"""
    body = await request.json()
    
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/alerts/{alert_id}"
    try:
        response = await client.put(fraud_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

@router.post("/fraud/alerts/{alert_id}/confirm", tags=["Fraud"])
async def confirm_fraud_alert(alert_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Confirm fraud alert"""
    body = await request.json()
    
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/alerts/{alert_id}/confirm"
    try:
        response = await client.post(fraud_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

@router.get("/fraud/velocity/{customer_id}", tags=["Fraud"])
async def check_velocity(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Check transaction velocity"""
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/velocity/{customer_id}"
    try:
        response = await client.get(fraud_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

@router.get("/fraud/statistics", tags=["Fraud"])
async def get_fraud_statistics(client: httpx.AsyncClient = Depends(get_http_client)):
    """Get fraud statistics"""
    fraud_url = f"{SERVICE_REGISTRY['fraud']}/api/fraud/statistics"
    try:
        response = await client.get(fraud_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Fraud Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Fraud Service unavailable")

# Document AI Advanced Routes
@router.post("/documents/{document_id}/extract", tags=["Document"])
async def extract_document(document_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Extract data from document"""
    body = await request.json()
    
    doc_url = f"{SERVICE_REGISTRY['document']}/api/documents/documents/{document_id}/extract"
    try:
        response = await client.post(doc_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Document Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Document Service unavailable")

@router.post("/documents/{document_id}/validate", tags=["Document"])
async def validate_document(document_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Validate document"""
    body = await request.json()
    
    doc_url = f"{SERVICE_REGISTRY['document']}/api/documents/documents/{document_id}/validate"
    try:
        response = await client.post(doc_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Document Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Document Service unavailable")

@router.get("/documents/customer/{customer_id}/summary", tags=["Document"])
async def get_customer_document_summary(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get customer document summary"""
    doc_url = f"{SERVICE_REGISTRY['document']}/api/documents/customers/{customer_id}/summary"
    try:
        response = await client.get(doc_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Document Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Document Service unavailable")

@router.get("/documents/statistics", tags=["Document"])
async def get_document_statistics(client: httpx.AsyncClient = Depends(get_http_client)):
    """Get document processing statistics"""
    doc_url = f"{SERVICE_REGISTRY['document']}/api/documents/statistics"
    try:
        response = await client.get(doc_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Document Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Document Service unavailable")

# Customer Advanced Routes
@router.get("/customers/{customer_id}/profile", tags=["Customer"])
async def get_customer_profile(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get customer profile"""
    customer_url = f"{SERVICE_REGISTRY['customer']}/customers/{customer_id}/profile"
    try:
        response = await client.get(customer_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Customer Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Customer Service unavailable")

@router.put("/customers/{customer_id}", tags=["Customer"])
async def update_customer(customer_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Update customer"""
    body = await request.json()
    
    customer_url = f"{SERVICE_REGISTRY['customer']}/customers/{customer_id}"
    try:
        response = await client.put(customer_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Customer Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Customer Service unavailable")

@router.post("/customers/{customer_id}/kyc-verify", tags=["Customer"])
async def verify_kyc(customer_id: str, request: Request, client: httpx.AsyncClient = Depends(get_http_client)):
    """Verify customer KYC"""
    body = await request.json()
    
    customer_url = f"{SERVICE_REGISTRY['customer']}/customers/{customer_id}/kyc-verify"
    try:
        response = await client.post(customer_url, json=body)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Customer Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Customer Service unavailable")

@router.get("/customers/{customer_id}/risk", tags=["Customer"])
async def get_customer_risk(customer_id: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """Get customer risk profile"""
    customer_url = f"{SERVICE_REGISTRY['customer']}/customers/{customer_id}/risk"
    try:
        response = await client.get(customer_url)
        return forward_response(response)
    except httpx.RequestError as e:
        logger.error(f"Customer Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Customer Service unavailable")

# Service Health Routes
@router.get("/services/health", tags=["Health"])
async def services_health(client: httpx.AsyncClient = Depends(get_http_client)):
    """Check health of all backend services"""
    health_status = {}
    
    for service_name, service_url in SERVICE_REGISTRY.items():
        try:
            health_url = f"{service_url}/health"
            response = await client.get(health_url, timeout=5.0)
            health_status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code
            }
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {str(e)}")
            health_status[service_name] = {
                "status": "unreachable",
                "error": str(e)
            }
    
    return health_status

# Gateway Health
@router.get("/health", tags=["Health"])
async def gateway_health():
    """Gateway health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": logger.info("Gateway health check")
    }
