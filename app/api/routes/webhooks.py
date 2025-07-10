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
    
    logger.info("🔔 Webhook endpoint called")
    
    try:
        # Check if bot is available
        if not hasattr(request.app.state, 'bot') or not hasattr(request.app.state, 'dp'):
            logger.error("❌ WEBHOOK: Bot not initialized, skipping webhook processing")
            return {"status": "bot_not_initialized", "message": "Bot not available"}
        
        # Get bot and dispatcher from app state
        bot = request.app.state.bot
        dp = request.app.state.dp
        
        if not bot or not dp:
            logger.error("❌ WEBHOOK: Bot or dispatcher is None")
            return {"status": "bot_not_available", "message": "Bot or dispatcher not available"}
        
        # Debug app state
        logger.info(f"✅ WEBHOOK: Bot object: {type(bot)}")
        logger.info(f"✅ WEBHOOK: Dispatcher object: {type(dp)}")
        
        # Get update data
        body = await request.json()
        logger.info(f"📨 WEBHOOK: Received update: {body}")
        
        update = Update(**body)
        
        # Log basic info about the update
        if update.message:
            user_id = update.message.from_user.id
            username = update.message.from_user.username or "no_username"
            text = update.message.text or "no_text"
            logger.info(f"💬 WEBHOOK: Message from @{username} (ID: {user_id}): '{text}'")
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
            username = update.callback_query.from_user.username or "no_username"
            data = update.callback_query.data or "no_data"
            logger.info(f"🔘 WEBHOOK: Callback from @{username} (ID: {user_id}): '{data}'")
        else:
            logger.info(f"❓ WEBHOOK: Unknown update type: {type(update)}")
        
        # Process update through dispatcher
        logger.info("⚙️ WEBHOOK: Processing through dispatcher...")
        result = await dp.feed_update(bot, update)
        logger.info(f"✅ WEBHOOK: Update processed successfully, result: {result}")
        
        return {"status": "ok", "processed": True}
        
    except Exception as e:
        logger.error(f"❌ WEBHOOK: Processing error: {e}")
        logger.exception("💥 WEBHOOK: Full error traceback:")
        return {"status": "error", "message": str(e)}


@router.get("/webhook")
async def webhook_info(request: Request):
    """Get webhook information"""
    
    try:
        if not hasattr(request.app.state, 'bot') or not request.app.state.bot:
            raise HTTPException(status_code=503, detail="Bot not initialized")
            
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
        if not hasattr(request.app.state, 'bot') or not request.app.state.bot:
            raise HTTPException(status_code=503, detail="Bot not initialized")
            
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
        if not hasattr(request.app.state, 'bot') or not request.app.state.bot:
            raise HTTPException(status_code=503, detail="Bot not initialized")
            
        bot = request.app.state.bot
        
        success = await bot.delete_webhook(drop_pending_updates=True)
        
        if success:
            return {"status": "webhook deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete webhook")
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook") 