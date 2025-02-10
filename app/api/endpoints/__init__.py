from .user_controller import router as user_router
from .recommended_workout_controller import router as recommended_workout_router

__all__ = ['user_router', 'recommended_workout_router']