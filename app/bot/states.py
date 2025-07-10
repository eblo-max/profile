"""Bot FSM states for conversation management"""

from aiogram.fsm.state import State, StatesGroup


class UserProfileStates(StatesGroup):
    """User profile setup states"""
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_relationship_status = State()
    waiting_for_interests = State()
    waiting_for_goals = State()


class TextAnalysisStates(StatesGroup):
    """Text analysis states"""
    waiting_for_text = State()
    waiting_for_context = State()
    analyzing = State()
    showing_results = State()


class PartnerProfileStates(StatesGroup):
    """Partner profile creation states - FULL version (28 questions in 6 blocks)"""
    # Introduction and consent
    intro = State()
    privacy_consent = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_basic_info = State()  # NEW: Age, occupation, etc.
    
    # Block 1: Narcissism and Grandiosity (7 questions)
    narcissism_q1 = State()  # Reaction to criticism
    narcissism_q2 = State()  # Attitude to success
    narcissism_q3 = State()  # Self-perception
    narcissism_q4 = State()  # Empathy to experiences
    narcissism_q5 = State()  # Relationships with others
    narcissism_q6 = State()  # Apologies and mistakes
    narcissism_q7 = State()  # Need for attention
    
    # Block 2: Control and Manipulation (8 questions)
    control_q1 = State()     # Time control
    control_q2 = State()     # Relationships with friends
    control_q3 = State()     # Access to information
    control_q4 = State()     # Financial control
    control_q5 = State()     # Reaction to boundaries
    control_q6 = State()     # Emotional blackmail
    control_q7 = State()     # Threats and intimidation
    control_q8 = State()     # Jealousy
    
    # Block 3: Gaslighting and Reality Distortion (6 questions)
    gaslighting_q1 = State() # Denial of events
    gaslighting_q2 = State() # Devaluation of feelings
    gaslighting_q3 = State() # Blame shifting
    gaslighting_q4 = State() # Using information
    gaslighting_q5 = State() # Double standards
    gaslighting_q6 = State() # Distorting words
    
    # Block 4: Emotional Regulation (5 questions)
    emotion_q1 = State()     # Anger management
    emotion_q2 = State()     # Emotional swings
    emotion_q3 = State()     # Ability to forgive
    emotion_q4 = State()     # Stress resistance
    emotion_q5 = State()     # Emotional support
    
    # Block 5: Intimacy and Coercion (4 questions)
    intimacy_q1 = State()    # Consent and coercion
    intimacy_q2 = State()    # Using intimacy
    intimacy_q3 = State()    # Appearance control
    intimacy_q4 = State()    # Jealousy about past
    
    # Block 6: Social Behavior (4 questions)
    social_q1 = State()      # Behavior alone vs public
    social_q2 = State()      # Attitude to staff
    social_q3 = State()      # Ability to friendship
    social_q4 = State()      # Work relationships
    
    # Processing and results
    reviewing_answers = State()
    processing = State()
    profile_complete = State()
    detailed_view = State()


class CompatibilityTestStates(StatesGroup):
    """Compatibility test states"""
    selecting_profiles = State()
    
    # Self-assessment questions
    self_q1 = State()   # Communication preferences
    self_q2 = State()   # Conflict handling
    self_q3 = State()   # Emotional needs
    self_q4 = State()   # Lifestyle compatibility
    self_q5 = State()   # Future goals
    self_q6 = State()   # Values alignment
    self_q7 = State()   # Intimacy preferences
    self_q8 = State()   # Personal growth
    self_q9 = State()   # Social preferences
    self_q10 = State()  # Deal breakers
    
    # Partner assessment questions
    partner_q1 = State()
    partner_q2 = State()
    partner_q3 = State()
    partner_q4 = State()
    partner_q5 = State()
    partner_q6 = State()
    partner_q7 = State()
    partner_q8 = State()
    partner_q9 = State()
    partner_q10 = State()
    
    analyzing_compatibility = State()
    showing_results = State()


class ProfileEditStates(StatesGroup):
    """Profile editing states"""
    select_field = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_interests = State()
    waiting_for_goals = State()
    waiting_for_bio = State()
    confirming_changes = State()


class PaymentStates(StatesGroup):
    """Payment process states"""
    selecting_plan = State()
    confirming_purchase = State()
    processing_payment = State()
    payment_success = State()
    payment_failed = State()


class ContentCreationStates(StatesGroup):
    """Admin content creation states"""
    waiting_for_type = State()
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_category = State()
    waiting_for_tags = State()
    reviewing_content = State()


class BroadcastStates(StatesGroup):
    """Admin broadcast states"""
    waiting_for_message = State()
    selecting_audience = State()
    confirming_broadcast = State()
    broadcasting = State()


class FeedbackStates(StatesGroup):
    """User feedback states"""
    waiting_for_rating = State()
    waiting_for_comment = State()
    waiting_for_suggestion = State()


class SupportStates(StatesGroup):
    """User support states"""
    waiting_for_issue = State()
    waiting_for_details = State()
    ticket_created = State()


class OnboardingStates(StatesGroup):
    """User onboarding states"""
    welcome = State()
    explain_features = State()
    setup_profile = State()
    first_analysis = State()
    onboarding_complete = State()


class SettingsStates(StatesGroup):
    """User settings states"""
    main_menu = State()
    notification_settings = State()
    privacy_settings = State()
    language_settings = State()
    theme_settings = State()


class QuestionnaireStates(StatesGroup):
    """Generic questionnaire states"""
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()
    question_5 = State()
    question_6 = State()
    question_7 = State()
    question_8 = State()
    question_9 = State()
    question_10 = State()
    question_11 = State()
    question_12 = State()
    question_13 = State()
    question_14 = State()
    question_15 = State()
    question_16 = State()
    question_17 = State()
    question_18 = State()
    question_19 = State()
    question_20 = State()
    
    reviewing = State()
    complete = State()


class ProfilerStates(StatesGroup):
    """Profiler states"""
    answering_questions = State()
    processing = State()
    results_ready = State()


class AdminStates(StatesGroup):
    """Admin panel states"""
    main_menu = State()
    user_management = State()
    content_management = State()
    analytics_view = State()
    system_settings = State()
    
    # User actions
    viewing_user = State()
    editing_user = State()
    user_actions = State()
    
    # Content actions
    content_list = State()
    content_edit = State()
    content_create = State()
    
    # Analytics
    stats_overview = State()
    detailed_analytics = State()
    export_data = State()


class ChatImportStates(StatesGroup):
    """Chat import and analysis states"""
    waiting_for_file = State()
    processing_file = State()
    selecting_analysis_type = State()
    analyzing_chat = State()
    showing_chat_results = State()


class AchievementStates(StatesGroup):
    """Achievement system states"""
    viewing_achievements = State()
    achievement_details = State()
    claiming_reward = State()


class NotificationStates(StatesGroup):
    """Notification management states"""
    main_settings = State()
    time_selection = State()
    frequency_selection = State()
    content_preferences = State()


# State groups mapping for easier access
STATE_GROUPS = {
    'profile': UserProfileStates,
    'analysis': TextAnalysisStates,
    'partner': PartnerProfileStates,
    'compatibility': CompatibilityTestStates,
    'edit': ProfileEditStates,
    'payment': PaymentStates,
    'content': ContentCreationStates,
    'broadcast': BroadcastStates,
    'feedback': FeedbackStates,
    'support': SupportStates,
    'onboarding': OnboardingStates,
    'settings': SettingsStates,
    'questionnaire': QuestionnaireStates,
    'profiler': ProfilerStates,
    'admin': AdminStates,
    'chat_import': ChatImportStates,
    'achievements': AchievementStates,
    'notifications': NotificationStates,
}


def get_state_group(group_name: str):
    """Get state group by name"""
    return STATE_GROUPS.get(group_name) 