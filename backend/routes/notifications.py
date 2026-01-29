import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from auth.jwt import get_current_user_id
from models import PushSubscription
from schemas.input_output_validation import validate_push_subscription_input, PushSubscriptionInput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["notifications"])


@router.post("/notifications/subscribe")
def subscribe_to_notifications(
    request_data: PushSubscriptionInput,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    """Subscribe a user to push notifications"""
    # Extract the values from the validated request body
    endpoint = request_data.endpoint
    p256dh = request_data.p256dh
    auth = request_data.auth

    logger.info(f"Subscribing user {user_id} to push notifications")

    try:
        # Validate input
        validate_push_subscription_input(user_id, endpoint, p256dh, auth)

        # Check if subscription already exists for this user
        existing_subscription = session.exec(
            select(PushSubscription).where(PushSubscription.user_id == user_id)
        ).first()

        if existing_subscription:
            # Update existing subscription
            existing_subscription.endpoint = endpoint
            existing_subscription.p256dh = p256dh
            existing_subscription.auth = auth
            session.add(existing_subscription)
        else:
            # Create new subscription
            subscription = PushSubscription(
                user_id=user_id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth
            )
            session.add(subscription)

        session.commit()
        logger.info(f"Successfully subscribed user {user_id} to push notifications")

        return {"status": "success", "message": "Successfully subscribed to notifications"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subscribing user {user_id} to notifications: {str(e)}")
        raise


@router.delete("/notifications/unsubscribe")
def unsubscribe_from_notifications(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    """Unsubscribe a user from push notifications"""
    logger.info(f"Unsubscribing user {user_id} from push notifications")

    try:
        # Find subscription for the user
        subscription = session.exec(
            select(PushSubscription).where(PushSubscription.user_id == user_id)
        ).first()

        if not subscription:
            logger.warning(f"No subscription found for user {user_id}")
            raise HTTPException(status_code=404, detail="No subscription found")

        # Delete the subscription
        session.delete(subscription)
        session.commit()

        logger.info(f"Successfully unsubscribed user {user_id} from push notifications")

        return {"status": "success", "message": "Successfully unsubscribed from notifications"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing user {user_id} from notifications: {str(e)}")
        raise