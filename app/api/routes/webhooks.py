"""Webhook endpoints for Telegram bot"""

from fastapi import APIRouter, Request, HTTPException, Depends
from aiogram.types import Update
from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    
    try:
        # Get bot and dispatcher from app state
        bot = request.app.state.bot
        dp = request.app.state.dp
        
        # Get update data
        body = await request.json()
        update = Update(**body)
        
        # Process update
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/webhook")
async def webhook_info(request: Request):
    """Get webhook information"""
    
    try:
        bot = request.app.state.bot
        webhook_info = await bot.get_webhook_info()
        
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook info")


@router.post("/webhook/set")
async def set_webhook(request: Request):
    """Set webhook URL"""
    
    if not settings.WEBHOOK_URL:
        raise HTTPException(status_code=400, detail="WEBHOOK_URL not configured")
    
    try:
        bot = request.app.state.bot
        
        webhook_url = f"{settings.WEBHOOK_URL}/webhook"
        success = await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        
        if success:
            return {
                "status": "success",
                "webhook_url": webhook_url
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set webhook")
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to set webhook")


@router.delete("/webhook")
async def delete_webhook(request: Request):
    """Delete webhook (switch to polling)"""
    
    try:
        bot = request.app.state.bot
        
        success = await bot.delete_webhook(drop_pending_updates=True)
        
        if success:
            return {"status": "webhook deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete webhook")
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook") 