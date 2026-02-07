"""
Analytics Service.

Provides comprehensive analytics and statistics for agents and admins.
"""
from typing import Dict, Any, List
from uuid import UUID
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case

from app.models.itinerary import Itinerary, ItineraryStatusEnum
from app.models.user import User, UserRoleEnum
from app.models.email_log import EmailLog
from app.models.activity_log import ActivityLog, ActivityActions


class AnalyticsService:
    """Service for analytics and statistics."""

    def get_agent_stats(self, user_id: UUID, db: Session) -> Dict[str, Any]:
        """
        Get real-time stats for an agent's dashboard.

        Returns today's activity and overall overview.
        """
        today = date.today()

        # TODAY'S ACTIVITY
        itineraries_created_today = db.query(Itinerary).filter(
            Itinerary.created_by_user_id == user_id,
            func.date(Itinerary.created_at) == today
        ).count()

        # Use ActivityLog with correct field names (action, created_at instead of action_type, timestamp)
        itineraries_edited_today = db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.action == ActivityActions.UPDATE,
            ActivityLog.entity_type == "itinerary",
            func.date(ActivityLog.created_at) == today
        ).count()

        # Use EmailLog instead of Email (which doesn't exist)
        emails_sent_today = db.query(EmailLog).filter(
            EmailLog.sent_by_user_id == user_id,
            func.date(EmailLog.sent_at) == today
        ).count()

        departures_today = db.query(Itinerary).filter(
            Itinerary.assigned_to_user_id == user_id,
            Itinerary.departure_date == today
        ).count()

        # OVERVIEW
        total_itineraries = db.query(Itinerary).filter(
            Itinerary.created_by_user_id == user_id
        ).count()

        incomplete_count = db.query(Itinerary).filter(
            Itinerary.assigned_to_user_id == user_id,
            Itinerary.status == ItineraryStatusEnum.DRAFT
        ).count()

        complete_count = db.query(Itinerary).filter(
            Itinerary.assigned_to_user_id == user_id,
            Itinerary.status == ItineraryStatusEnum.COMPLETED
        ).count()

        # UPCOMING DEPARTURES
        upcoming = db.query(Itinerary).filter(
            Itinerary.assigned_to_user_id == user_id,
            Itinerary.departure_date >= today,
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.SENT])
        ).order_by(Itinerary.departure_date.asc()).limit(10).all()

        upcoming_departures = [
            {
                'id': str(itin.id),
                'title': itin.tour_title,
                'departure_date': itin.departure_date.isoformat(),
                'days_until': (itin.departure_date - today).days,
                'traveler': itin.travelers[0].full_name if itin.travelers else 'Unknown'
            }
            for itin in upcoming
        ]

        # RECENT ACTIVITY - use correct field names
        recent_activities = db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(ActivityLog.created_at.desc()).limit(10).all()

        recent_activity_list = [
            {
                'action': act.action,
                'description': act.description,
                'timestamp': act.created_at.isoformat(),
                'entity_id': str(act.entity_id) if act.entity_id else None,
                'entity_type': act.entity_type
            }
            for act in recent_activities
        ]

        return {
            'today': {
                'itineraries_created': itineraries_created_today,
                'itineraries_edited': itineraries_edited_today,
                'emails_sent': emails_sent_today,
                'departures_today': departures_today
            },
            'overview': {
                'total_itineraries': total_itineraries,
                'incomplete_count': incomplete_count,
                'complete_count': complete_count
            },
            'upcoming_departures': upcoming_departures,
            'recent_activity': recent_activity_list
        }

    def get_agent_analytics(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get historical analytics for an agent over a date range.
        """
        # Itineraries created over time
        itineraries = db.query(
            func.date(Itinerary.created_at).label('date'),
            func.count(Itinerary.id).label('count')
        ).filter(
            Itinerary.created_by_user_id == user_id,
            func.date(Itinerary.created_at) >= date_from,
            func.date(Itinerary.created_at) <= date_to
        ).group_by(func.date(Itinerary.created_at)).all()

        itineraries_over_time = [
            {'date': str(row.date), 'count': row.count}
            for row in itineraries
        ]

        # Status breakdown
        status_breakdown = db.query(
            Itinerary.status,
            func.count(Itinerary.id).label('count')
        ).filter(
            Itinerary.created_by_user_id == user_id,
            func.date(Itinerary.created_at) >= date_from,
            func.date(Itinerary.created_at) <= date_to
        ).group_by(Itinerary.status).all()

        status_summary = {
            row.status.value: row.count
            for row in status_breakdown
        }

        # Most used tours - use tour_title instead of title
        popular_tours = db.query(
            Itinerary.tour_title,
            func.count(Itinerary.id).label('count')
        ).filter(
            Itinerary.created_by_user_id == user_id,
            func.date(Itinerary.created_at) >= date_from,
            func.date(Itinerary.created_at) <= date_to
        ).group_by(Itinerary.tour_title).order_by(
            func.count(Itinerary.id).desc()
        ).limit(5).all()

        popular_tours_list = [
            {'title': row.tour_title, 'count': row.count}
            for row in popular_tours
        ]

        return {
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'itineraries_over_time': itineraries_over_time,
            'status_breakdown': status_summary,
            'popular_tours': popular_tours_list,
            'total_itineraries': sum(status_summary.values()) if status_summary else 0
        }

    def get_admin_stats(self, db: Session) -> Dict[str, Any]:
        """
        Get real-time stats for admin dashboard.

        Company-wide statistics.
        """
        today = date.today()

        # TODAY'S ACTIVITY
        total_itineraries_created_today = db.query(Itinerary).filter(
            func.date(Itinerary.created_at) == today
        ).count()

        # Use EmailLog instead of Email
        total_emails_sent_today = db.query(EmailLog).filter(
            func.date(EmailLog.sent_at) == today
        ).count()

        active_agents = db.query(User).filter(
            User.role == UserRoleEnum.CS_AGENT,
            User.is_active == True
        ).count()

        departures_today = db.query(Itinerary).filter(
            Itinerary.departure_date == today
        ).count()

        # OVERVIEW
        total_itineraries_all_time = db.query(Itinerary).count()

        total_agents = db.query(User).filter(
            User.role == UserRoleEnum.CS_AGENT
        ).count()

        from app.models.itinerary import Traveler
        total_travelers = db.query(Traveler).count()

        # PER AGENT TODAY
        agent_activity = db.query(
            User.full_name,
            func.count(Itinerary.id).label('itineraries_created')
        ).join(
            Itinerary, Itinerary.created_by_user_id == User.id
        ).filter(
            func.date(Itinerary.created_at) == today
        ).group_by(User.full_name).all()

        per_agent_today = [
            {'agent': row.full_name, 'itineraries_created': row.itineraries_created}
            for row in agent_activity
        ]

        return {
            'today': {
                'total_itineraries_created': total_itineraries_created_today,
                'total_emails_sent': total_emails_sent_today,
                'active_agents': active_agents,
                'departures_today': departures_today
            },
            'overview': {
                'total_itineraries_all_time': total_itineraries_all_time,
                'total_agents': total_agents,
                'total_travelers': total_travelers
            },
            'per_agent_today': per_agent_today
        }

    def get_company_analytics(
        self,
        date_from: date,
        date_to: date,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get company-wide analytics over a date range.

        Popular destinations, accommodations, agent performance.
        """
        # Most popular destinations
        from app.models.itinerary import ItineraryDay, itinerary_day_destinations
        from app.models.destination import Destination

        popular_destinations = db.query(
            Destination.name,
            func.count(itinerary_day_destinations.c.destination_id).label('count')
        ).join(
            itinerary_day_destinations,
            Destination.id == itinerary_day_destinations.c.destination_id
        ).join(
            ItineraryDay,
            ItineraryDay.id == itinerary_day_destinations.c.itinerary_day_id
        ).join(
            Itinerary,
            Itinerary.id == ItineraryDay.itinerary_id
        ).filter(
            func.date(Itinerary.created_at) >= date_from,
            func.date(Itinerary.created_at) <= date_to
        ).group_by(Destination.name).order_by(
            func.count(itinerary_day_destinations.c.destination_id).desc()
        ).limit(10).all()

        popular_destinations_list = [
            {'destination': row.name, 'count': row.count}
            for row in popular_destinations
        ]

        # Agent performance comparison
        agent_performance = db.query(
            User.full_name,
            func.count(Itinerary.id).label('total_itineraries'),
            func.count(func.nullif(Itinerary.status == ItineraryStatusEnum.COMPLETED, False)).label('completed')
        ).join(
            Itinerary, Itinerary.created_by_user_id == User.id
        ).filter(
            User.role == UserRoleEnum.CS_AGENT,
            func.date(Itinerary.created_at) >= date_from,
            func.date(Itinerary.created_at) <= date_to
        ).group_by(User.full_name).all()

        agent_performance_list = [
            {
                'agent': row.full_name,
                'total_itineraries': row.total_itineraries,
                'completed': row.completed or 0,
                'completion_rate': round((row.completed or 0) / row.total_itineraries * 100, 1) if row.total_itineraries > 0 else 0
            }
            for row in agent_performance
        ]

        # Itineraries over time (weekly)
        itineraries_weekly = db.query(
            func.date_trunc('week', Itinerary.created_at).label('week'),
            func.count(Itinerary.id).label('count')
        ).filter(
            func.date(Itinerary.created_at) >= date_from,
            func.date(Itinerary.created_at) <= date_to
        ).group_by(func.date_trunc('week', Itinerary.created_at)).all()

        itineraries_over_time = [
            {'week': str(row.week), 'count': row.count}
            for row in itineraries_weekly
        ]

        return {
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'popular_destinations': popular_destinations_list,
            'agent_performance': agent_performance_list,
            'itineraries_over_time': itineraries_over_time
        }


# Create singleton instance
analytics_service = AnalyticsService()
