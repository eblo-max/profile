"""Bot keyboards for user interface"""

from .inline import (
    main_menu_kb,
    analysis_menu_kb,
    profiler_menu_kb,
    compatibility_menu_kb,
    daily_menu_kb,
    profile_menu_kb,
    subscription_menu_kb,
    admin_menu_kb,
    confirmation_kb,
    back_to_main_kb,
    skip_kb,
    gender_kb,
    age_group_kb,
    relationship_status_kb,
    notification_settings_kb
)

from .reply import (
    share_contact_kb,
    cancel_kb,
    main_menu_reply_kb
)

__all__ = [
    # Inline keyboards
    "main_menu_kb",
    "analysis_menu_kb", 
    "profiler_menu_kb",
    "compatibility_menu_kb",
    "daily_menu_kb",
    "profile_menu_kb",
    "subscription_menu_kb",
    "admin_menu_kb",
    "confirmation_kb",
    "back_to_main_kb",
    "skip_kb",
    "gender_kb",
    "age_group_kb",
    "relationship_status_kb",
    "notification_settings_kb",
    
    # Reply keyboards
    "share_contact_kb",
    "cancel_kb",
    "main_menu_reply_kb"
] 