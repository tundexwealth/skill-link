import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from datetime import timedelta
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from db.session import SessionLocal
from models import AuthSession, Category, ClaimRequest, Location, Provider, Service, User, Rating
from queries import categories, services_display, top_six_services, total_services_count, total_all_services_count, provider_info, check_other_providers, all_providers_display, get_provider_average_rating, get_all_ratings_for_provider
from security import hash_password, hash_session_token, new_session_token, session_has_expired, utc_now, verify_password

router = APIRouter(prefix="/api/v1", tags=["BACKEND_API v1"])


class ProviderServiceRequest(BaseModel):
    category_id: int
    service_title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=5)
    price: Optional[str] = None
    image_url: Optional[str] = None


class ProviderRegistryRequest(BaseModel):
    business_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=5)
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    services: list[ProviderServiceRequest] = Field(..., min_length=1)
    area: Optional[str] = None
    city: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2)
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class ProviderImportRequest(BaseModel):
    business_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=5)
    email: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    about: Optional[str] = None
    imported_from: Optional[str] = None
    services: Optional[list[ProviderServiceRequest]] = None
    area: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=10, max_length=256)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=1, max_length=256)


class ProviderProfileUpdate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=160)
    phone: str = Field(..., min_length=5, max_length=40)
    website: Optional[str] = Field(None, max_length=2048)
    linkedin_url: Optional[str] = Field(None, max_length=2048)
    about: Optional[str] = Field(None, max_length=3000)
    logo_url: Optional[str] = Field(None, max_length=2048)
    cover_image: Optional[str] = Field(None, max_length=2048)


class RatingRequest(BaseModel):
    provider_id: int
    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    email: Optional[str] = Field(None, max_length=255)


def _validate_password(password: str) -> None:
    if not all((re.search(r"[a-z]", password), re.search(r"[A-Z]", password), re.search(r"\d", password))):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must include uppercase, lowercase, and a number.")


def _current_user(request: Request) -> User:
    token = request.cookies.get("skill_link_session")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in first.")
    db = SessionLocal()
    try:
        session = db.query(AuthSession).filter(AuthSession.token_hash == hash_session_token(token)).first()
        if session is None or session_has_expired(session.expires_at):
            if session is not None:
                db.delete(session)
                db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired. Please sign in again.")
        user = db.get(User, session.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found.")
        db.expunge(user)
        return user
    finally:
        db.close()


def _require_admin_user(user: User) -> User:
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return user


def _service_data(service: Service) -> dict:
    return {"id": service.id, "title": service.title, "description": service.description, "price": service.price,
            "image_url": service.image_url, "category_id": service.category_id,
            "category_name": service.category.name if service.category else None, "location_id": service.location_id}


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterRequest, response: Response):
    _validate_password(payload.password)
    db = SessionLocal()
    try:
        email, username = payload.email.strip().lower(), payload.username.strip()
        if db.query(User).filter((User.email == email) | (User.username == username)).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with that email or username already exists.")
        user = User(username=username, email=email, password=hash_password(payload.password))
        db.add(user)
        db.flush()
        token = new_session_token()
        db.add(AuthSession(user_id=user.id, token_hash=hash_session_token(token), expires_at=utc_now() + timedelta(days=7)))
        db.commit()
        response.set_cookie("skill_link_session", token, httponly=True, samesite="lax", max_age=604800, path="/")
        return {"user": {"id": user.id, "username": user.username, "email": user.email}}
    except HTTPException:
        db.rollback()
        raise
    finally:
        db.close()


@router.post("/auth/login")
async def login_user(payload: LoginRequest, response: Response):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
        if user is None or not verify_password(payload.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        token = new_session_token()
        db.add(AuthSession(user_id=user.id, token_hash=hash_session_token(token), expires_at=utc_now() + timedelta(days=7)))
        db.commit()
        response.set_cookie("skill_link_session", token, httponly=True, samesite="lax", max_age=604800, path="/")
        return {"user": {"id": user.id, "username": user.username, "email": user.email}}
    finally:
        db.close()


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(request: Request, response: Response):
    token = request.cookies.get("skill_link_session")
    if token:
        db = SessionLocal()
        try:
            db.query(AuthSession).filter(AuthSession.token_hash == hash_session_token(token)).delete()
            db.commit()
        finally:
            db.close()
    response.delete_cookie("skill_link_session", path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.get("/auth-check")
async def check_auth(request: Request):
    token = request.cookies.get("skill_link_session")
    if not token:
        return {"authenticated": False}
    db = SessionLocal()
    try:
        session = db.query(AuthSession).filter(AuthSession.token_hash == hash_session_token(token)).first()
        if session is None or session_has_expired(session.expires_at):
            if session is not None:
                db.delete(session)
                db.commit()
            return {"authenticated": False}
        return {"authenticated": True}
    finally:
        db.close()

@router.get("/auth/me")
async def current_account(user: User = Depends(_current_user)):
    return {"user": {"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}}


@router.get("/admin/dashboard")
async def admin_dashboard(user: User = Depends(_current_user)):
    _require_admin_user(user)
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_providers = db.query(Provider).count()
        verified_providers = db.query(Provider).filter(Provider.verified.is_(True)).count()
        pending_providers = total_providers - verified_providers
        pending_claim_requests = db.query(ClaimRequest).filter(ClaimRequest.status == "pending").count()
        return {
            "total_users": total_users,
            "total_providers": total_providers,
            "verified_providers": verified_providers,
            "pending_providers": pending_providers,
            "pending_claim_requests": pending_claim_requests,
        }
    finally:
        db.close()


@router.get("/admin/providers")
async def admin_providers(
    user: User = Depends(_current_user),
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
):
    _require_admin_user(user)
    db = SessionLocal()
    try:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        query = db.query(Provider)
        if search:
            term = search.strip()
            if term.isdigit():
                query = query.filter(
                    or_(
                        Provider.id == int(term),
                        Provider.business_name.ilike(f"%{term}%"),
                    )
                )
            else:
                query = query.filter(Provider.business_name.ilike(f"%{term}%"))

        total = query.count()
        providers = query.order_by(Provider.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "providers": [
                {
                    "id": provider.id,
                    "business_name": provider.business_name,
                    "email": provider.email,
                    "phone": provider.phone,
                    "verified": provider.verified,
                    "verification_status": "verified" if provider.verified else "unverified",
                    "is_imported": provider.is_imported,
                    "imported_from": provider.imported_from,
                    "is_pending": not provider.verified,
                    "created_at": provider.created_at.isoformat() if provider.created_at else None,
                }
                for provider in providers
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    finally:
        db.close()


@router.post("/admin/providers/{provider_id}/verify")
async def verify_provider(provider_id: int, user: User = Depends(_current_user)):
    _require_admin_user(user)
    db = SessionLocal()
    try:
        provider = db.get(Provider, provider_id)
        if provider is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
        provider.verified = True
        db.commit()
        db.refresh(provider)
        return {
            "message": "Provider verified successfully",
            "provider_id": provider.id,
            "verified": provider.verified,
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()


@router.post("/admin/providers/{provider_id}/unverify")
async def unverify_provider(provider_id: int, user: User = Depends(_current_user)):
    _require_admin_user(user)
    db = SessionLocal()
    try:
        provider = db.get(Provider, provider_id)
        if provider is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
        provider.verified = False
        db.commit()
        db.refresh(provider)
        return {
            "message": "Provider verification revoked successfully",
            "provider_id": provider.id,
            "verified": provider.verified,
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()


@router.get("/providers/{provider_id}/claim-status")
async def provider_claim_status(provider_id: int, user: User = Depends(_current_user)):
    db = SessionLocal()
    try:
        claim = db.query(ClaimRequest).filter(
            ClaimRequest.provider_id == provider_id,
            ClaimRequest.user_id == user.id
        ).order_by(ClaimRequest.created_at.desc()).first()

        if claim is None:
            return {"status": "none"}

        return {
            "status": claim.status,
            "claim_request_id": claim.id,
            "created_at": claim.created_at.isoformat(),
            "updated_at": claim.updated_at.isoformat(),
        }
    finally:
        db.close()


@router.post("/providers/{provider_id}/claim")
async def claim_provider(provider_id: int, user: User = Depends(_current_user)):
    db = SessionLocal()
    try:
        provider = db.get(Provider, provider_id)
        if provider is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
        if provider.verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This provider is already verified.")
        if provider.user_id == user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already own this provider profile.")
        if db.query(Provider).filter(Provider.user_id == user.id).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already own a provider profile.")

        existing_claim = db.query(ClaimRequest).filter(
            ClaimRequest.provider_id == provider_id,
            ClaimRequest.user_id == user.id,
            ClaimRequest.status.in_(["pending", "approved"])
        ).first()

        if existing_claim is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already have an active claim request for this provider.")

        claim = ClaimRequest(user_id=user.id, provider_id=provider_id, status="pending")
        db.add(claim)
        db.commit()
        db.refresh(claim)
        return {
            "message": "Claim request submitted successfully.",
            "claim_request_id": claim.id,
            "status": claim.status,
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()


@router.get("/admin/claim_requests")
async def admin_claim_requests(user: User = Depends(_current_user)):
    _require_admin_user(user)
    db = SessionLocal()
    try:
        claim_requests = db.query(ClaimRequest).filter(ClaimRequest.status == "pending").order_by(ClaimRequest.created_at.desc()).all()
        return {
            "claim_requests": [
                {
                    "id": claim.id,
                    "provider_id": claim.provider_id,
                    "provider_name": claim.provider.business_name if claim.provider else None,
                    "user_id": claim.user_id,
                    "username": claim.user.username if claim.user else None,
                    "email": claim.user.email if claim.user else None,
                    "status": claim.status,
                    "created_at": claim.created_at.isoformat(),
                }
                for claim in claim_requests
            ]
        }
    finally:
        db.close()


@router.post("/admin/claim_requests/{claim_request_id}/approve")
async def admin_approve_claim_request(claim_request_id: int, user: User = Depends(_current_user)):
    _require_admin_user(user)
    db = SessionLocal()
    try:
        claim = db.get(ClaimRequest, claim_request_id)
        if claim is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim request not found")
        if claim.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Claim request has already been processed.")
        provider = db.get(Provider, claim.provider_id)
        if provider is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

        provider.verified = True
        provider.user_id = claim.user_id
        claim.status = "approved"
        claim.updated_at = utc_now()

        db.query(ClaimRequest).filter(
            ClaimRequest.provider_id == provider.id,
            ClaimRequest.status == "pending",
            ClaimRequest.id != claim.id
        ).update({
            ClaimRequest.status: "rejected",
            ClaimRequest.updated_at: utc_now()
        }, synchronize_session=False)

        db.commit()
        db.refresh(claim)
        return {
            "message": "Claim request approved.",
            "claim_request_id": claim.id,
            "provider_id": provider.id,
            "verified": provider.verified,
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()


@router.post("/admin/claim_requests/{claim_request_id}/reject")
async def admin_reject_claim_request(claim_request_id: int, user: User = Depends(_current_user)):
    _require_admin_user(user)
    db = SessionLocal()
    try:
        claim = db.get(ClaimRequest, claim_request_id)
        if claim is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim request not found")
        if claim.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Claim request has already been processed.")

        claim.status = "rejected"
        claim.updated_at = utc_now()
        db.commit()
        db.refresh(claim)
        return {
            "message": "Claim request rejected.",
            "claim_request_id": claim.id,
            "status": claim.status,
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()


@router.post("/providers", status_code=status.HTTP_201_CREATED)
async def create_provider(payload: ProviderRegistryRequest, user: User = Depends(_current_user)):
    db = SessionLocal()

    try:
        if db.query(Provider).filter(Provider.user_id == user.id).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already have a provider profile. Manage it from My Profile.")
        categories_by_id = {}
        for service_payload in payload.services:
            category = db.get(Category, service_payload.category_id)
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category {service_payload.category_id} not found"
                )
            categories_by_id[category.id] = category

        provider = Provider(
            user_id=user.id,
            business_name=payload.business_name.strip(),
            phone=payload.phone.strip(),
            website=payload.website.strip() if payload.website else None,
            linkedin_url=payload.linkedin_url.strip() if payload.linkedin_url else None,
            email=user.email,
        )
        location = Location(
            area=payload.area.strip() if payload.area else None,
            city=payload.city.strip(),
            state=payload.state.strip(),
            address=payload.address.strip() if payload.address else None,
            longitude=payload.longitude,
            latitude=payload.latitude,
        )

        db.add(provider)
        db.add(location)
        db.flush()

        services = []
        for service_payload in payload.services:
            category = categories_by_id[service_payload.category_id]
            service = Service(
                title=service_payload.service_title.strip(),
                image_url=(service_payload.image_url.strip() if service_payload.image_url else category.image_url),
                description=service_payload.description.strip(),
                price=service_payload.price.strip() if service_payload.price else None,
                provider_id=provider.id,
                location_id=location.id,
                category_id=category.id,
            )
            db.add(service)
            services.append(service)
        db.commit()
        db.refresh(provider)
        for service in services:
            db.refresh(service)

        return {
            "message": "Provider registered successfully",
            "provider": {
                "id": provider.id,
                "business_name": provider.business_name,
                "phone": provider.phone,
                "website": provider.website,
                "linkedin_url": provider.linkedin_url,
            },
            "services": [
                {
                    "id": service.id,
                    "title": service.title,
                    "category_id": service.category_id,
                    "location_id": service.location_id,
                }
                for service in services
            ],
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    finally:
        db.close()


@router.post("/providers/import", status_code=status.HTTP_201_CREATED)
async def import_provider(payload: ProviderImportRequest):
    db = SessionLocal()
    try:
        provider = Provider(
            user_id=None,
            business_name=payload.business_name.strip(),
            phone=payload.phone.strip(),
            email=payload.email.strip().lower() if payload.email else None,
            website=payload.website.strip() if payload.website else None,
            linkedin_url=payload.linkedin_url.strip() if payload.linkedin_url else None,
            about=payload.about.strip() if payload.about else None,
            is_imported=True,
            imported_from=payload.imported_from.strip() if payload.imported_from else "seed",
            verified=False,
        )
        db.add(provider)

        location = None
        if payload.city and payload.state:
            location = Location(
                area=payload.area.strip() if payload.area else None,
                city=payload.city.strip(),
                state=payload.state.strip(),
                address=payload.address.strip() if payload.address else None,
                longitude=payload.longitude,
                latitude=payload.latitude,
            )
            db.add(location)
            db.flush()

        db.flush()

        services = []
        if payload.services:
            categories_by_id = {}
            for service_payload in payload.services:
                category = db.get(Category, service_payload.category_id)
                if category is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Category {service_payload.category_id} not found"
                    )
                categories_by_id[category.id] = category

            for service_payload in payload.services:
                category = categories_by_id[service_payload.category_id]
                service = Service(
                    title=service_payload.service_title.strip(),
                    image_url=(service_payload.image_url.strip() if service_payload.image_url else category.image_url),
                    description=service_payload.description.strip(),
                    price=service_payload.price.strip() if service_payload.price else None,
                    provider_id=provider.id,
                    location_id=location.id if location else None,
                    category_id=category.id,
                )
                db.add(service)
                services.append(service)

        db.commit()
        db.refresh(provider)
        for service in services:
            db.refresh(service)

        return {
            "message": "Provider imported successfully",
            "provider": {
                "id": provider.id,
                "business_name": provider.business_name,
                "phone": provider.phone,
                "website": provider.website,
                "linkedin_url": provider.linkedin_url,
                "is_imported": provider.is_imported,
                "imported_from": provider.imported_from,
                "verified": provider.verified,
            },
            "services": [
                {
                    "id": service.id,
                    "title": service.title,
                    "category_id": service.category_id,
                    "location_id": service.location_id,
                }
                for service in services
            ],
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    finally:
        db.close()


@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: int, user: User = Depends(_current_user)):
    """Delete a provider and the services and location created for that provider."""
    db = SessionLocal()

    try:
        provider = db.get(Provider, provider_id)
        if provider is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found"
            )
        if provider.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own provider profile.")

        services = db.query(Service).filter(Service.provider_id == provider_id).all()
        location_ids = {service.location_id for service in services if service.location_id is not None}

        for service in services:
            db.delete(service)
        db.flush()

        # A location is normally shared by a provider's services. Only remove it
        # when no remaining service references it.
        for location_id in location_ids:
            is_still_used = db.query(Service.id).filter(Service.location_id == location_id).first()
            if is_still_used is None:
                location = db.get(Location, location_id)
                if location is not None:
                    db.delete(location)

        db.delete(provider)
        db.commit()
        return {"message": "Provider deleted successfully", "provider_id": provider_id}
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    finally:
        db.close()


@router.get("/providers/me")
async def get_my_provider(user: User = Depends(_current_user)):
    db = SessionLocal()
    try:
        provider = db.query(Provider).filter(Provider.user_id == user.id).first()
        if provider is None:
            return {"provider": None, "services": []}
        services = db.query(Service).filter(Service.provider_id == provider.id).all()
        return {
            "provider": {
                "id": provider.id, "business_name": provider.business_name, "phone": provider.phone,
                "website": provider.website, "linkedin_url": provider.linkedin_url,
                "about": provider.about, "logo_url": provider.logo_url, "cover_image": provider.cover_image,
                "email": provider.email, "verified": provider.verified,
                "created_at": provider.created_at.isoformat() if provider.created_at else None,
            },
            "services": [_service_data(service) for service in services],
        }
    finally:
        db.close()


@router.put("/providers/me")
async def update_my_provider(payload: ProviderProfileUpdate, user: User = Depends(_current_user)):
    db = SessionLocal()
    try:
        provider = db.query(Provider).filter(Provider.user_id == user.id).first()
        if provider is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Create a provider profile before editing it.")
        for field, value in payload.dict().items():
            setattr(provider, field, value.strip() if isinstance(value, str) else value)
        db.commit()
        return {"message": "Provider profile updated successfully."}
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()


@router.post("/providers/me/services", status_code=status.HTTP_201_CREATED)
async def add_my_service(payload: ProviderServiceRequest, user: User = Depends(_current_user)):
    db = SessionLocal()
    try:
        provider = db.query(Provider).filter(Provider.user_id == user.id).first()
        if provider is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Create a provider profile before adding services.")
        category = db.get(Category, payload.category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        existing_service = db.query(Service).filter(Service.provider_id == provider.id).first()
        if existing_service is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Your provider profile needs a location before a service can be added.")
        service = Service(
            title=payload.service_title.strip(), description=payload.description.strip(),
            price=payload.price.strip() if payload.price else None,
            image_url=payload.image_url.strip() if payload.image_url else category.image_url,
            category_id=category.id, provider_id=provider.id, location_id=existing_service.location_id,
        )
        db.add(service)
        db.commit()
        db.refresh(service)
        return {"service": _service_data(service)}
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()


@router.delete("/providers/me/services/{service_id}")
async def delete_my_service(service_id: int, user: User = Depends(_current_user)):
    db = SessionLocal()
    try:
        provider = db.query(Provider).filter(Provider.user_id == user.id).first()
        service = db.get(Service, service_id)
        if provider is None or service is None or service.provider_id != provider.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
        db.delete(service)
        db.commit()
        return {"message": "Service deleted successfully."}
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    finally:
        db.close()

@router.get("/top_six_services")
async def get_top_six_services():
    try:
        services = top_six_services()
        return {"top_six_services": services}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
@router.get("/categories")
async def get_categories(type: str = None):
    try:
        categories_list = categories(type)
        return {"categories": categories_list}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
@router.get("/categories/services")
async def get_services(
    category_id: str,
    page: int = 1,
    page_size: int = 25,
    query: str | None = None,
    location: str | None = None,
):
    if page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be 1 or greater.")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page size must be between 1 and 100.")

    try:
        if category_id == "all":
            services_list = all_providers_display(page=page, page_size=page_size, query=query, location=location)
            total = total_all_services_count(query=query, location=location)
        else:
            services_list = services_display(int(category_id), page=page, page_size=page_size, query=query, location=location)
            total = total_services_count(int(category_id), query=query, location=location)

        return {
            "services": services_list,
            "page": page,
            "page_size": page_size,
            "total": total,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/total_listings")
async def get_total_listings(category_id: str):
    try:
        if category_id == "all":
            total = total_all_services_count()
        else:
            try:
                total = total_services_count(int(category_id))
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id must be an integer or 'all'.")
        return {"total_listings": total}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
@router.get("/provider_services")
async def get_provider_services(provider_id: int):
    try:
        services_list = provider_info(provider_id)
        return {"services": services_list}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
@router.get("/other_provider_services")
async def get_other_provider_services(provider_id: int, page: int = 1, page_size: int = 3):
    if page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be 1 or greater.")
    if page_size < 1 or page_size > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page size must be between 1 and 10.")

    try:
        services_list = check_other_providers(provider_id, page=page, page_size=page_size)
        return {"services": services_list, "page": page, "page_size": page_size}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/ratings", status_code=status.HTTP_201_CREATED)
async def create_rating(payload: RatingRequest, request: Request):
    db = SessionLocal()
    try:
        token = request.cookies.get("skill_link_session")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        session = db.query(AuthSession).filter(
            AuthSession.token_hash == hash_session_token(token)
        ).first()

        if not session or session_has_expired(session.expires_at):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )

        user = db.get(User, session.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        provider = db.get(Provider, payload.provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found"
            )

        existing_rating = db.query(Rating).filter(
            Rating.user_id == user.id,
            Rating.provider_id == payload.provider_id
        ).first()

        if existing_rating:
            existing_rating.score = payload.score
            existing_rating.comment = payload.comment
            db.commit()
            return {"message": "Rating updated successfully", "rating_id": existing_rating.id}
        else:
            new_rating = Rating(
                user_id=user.id,
                provider_id=payload.provider_id,
                score=payload.score,
                comment=payload.comment
            )
            db.add(new_rating)
            db.commit()
            return {"message": "Rating created successfully", "rating_id": new_rating.id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        db.close()


@router.get("/ratings/{provider_id}")
async def get_provider_ratings(provider_id: int):
    db = SessionLocal()
    try:
        provider = db.get(Provider, provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found"
            )

        ratings = db.query(Rating).filter(
            Rating.provider_id == provider_id
        ).order_by(Rating.created_at.desc()).all()

        ratings_data = [
            {
                "id": r.id,
                "score": r.score,
                "comment": r.comment,
                "username": r.user.username if r.user else "Anonymous",
                "created_at": r.created_at.isoformat()
            }
            for r in ratings
        ]

        average_rating = sum(r.score for r in ratings) / len(ratings) if ratings else 0

        return {
            "ratings": ratings_data,
            "average_rating": round(average_rating, 1),
            "total_ratings": len(ratings)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        db.close()


@router.get("/provider_average_rating/{provider_id}")
async def get_provider_avg_rating(provider_id: int):
    db = SessionLocal()
    try:
        provider = db.get(Provider, provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found"
            )

        ratings = db.query(Rating).filter(
            Rating.provider_id == provider_id
        ).all()

        average_rating = sum(r.score for r in ratings) / len(ratings) if ratings else 0

        return {
            "average_rating": round(average_rating, 1),
            "total_ratings": len(ratings)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        db.close()
