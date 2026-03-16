from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta

from app.api.v1.deps import get_db, require_admin, require_cs_agent
from app.schemas.analytics import AnalyticsResponse
from app.models.itinerary import Itinerary, ItineraryStatusEnum, PaymentStatusEnum, Traveler
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cs_agent)
):
    """
    Get analytics dashboard data.
    Accessible by Admins and CS Agents.
    Returns tailored data based on user role.
    """
    from app.services.analytics_service import analytics_service
    from app.models.user import UserRoleEnum

    now = datetime.utcnow()
    last_month = now - timedelta(days=30)
    date_from = (now - timedelta(days=30)).date()
    date_to = now.date()

    # ==================== ADMIN VIEW ====================
    if current_user.role == UserRoleEnum.ADMIN:
        # Get real-time admin stats
        admin_today = analytics_service.get_admin_stats(db)
        
        # Get company-wide historical analytics
        company_analytics = analytics_service.get_company_analytics(date_from, date_to, db)
        
        # Calculate Overview Metrics (System Wide)
        # Using the same logic as before but cleaner
        
        # Revenue
        total_revenue = db.query(func.sum(Itinerary.total_price)).filter(
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
        ).scalar() or 0
        total_revenue = float(total_revenue)
        
        prev_revenue = db.query(func.sum(Itinerary.total_price)).filter(
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED]),
            Itinerary.created_at < last_month
        ).scalar() or 0
        prev_revenue = float(prev_revenue)
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0.0

        # Bookings
        total_bookings = db.query(func.count(Itinerary.id)).filter(
            Itinerary.status != ItineraryStatusEnum.DRAFT
        ).scalar() or 0
        
        prev_bookings = db.query(func.count(Itinerary.id)).filter(
            Itinerary.status != ItineraryStatusEnum.DRAFT,
            Itinerary.created_at < last_month
        ).scalar() or 0
        bookings_growth = ((total_bookings - prev_bookings) / prev_bookings * 100) if prev_bookings > 0 else 0.0

        # Active Customers
        active_customers = db.query(func.count(func.distinct(Traveler.email))).join(Itinerary).filter(
            Traveler.is_primary == True,
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.SENT])
        ).scalar() or 0
        
        avg_booking_val = (total_revenue / total_bookings) if total_bookings > 0 else 0.0

        # Payment Metrics
        total_paid = float(db.query(func.sum(Itinerary.deposit_amount)).filter(
            Itinerary.payment_status == PaymentStatusEnum.FULLY_PAID
        ).scalar() or 0)
        
        total_deposits = float(db.query(func.sum(Itinerary.deposit_amount)).filter(
            Itinerary.payment_status == PaymentStatusEnum.PARTIALLY_PAID
        ).scalar() or 0)
        
        total_pending = total_revenue - (total_paid + total_deposits)

        # Status Breakdown
        status_counts = db.query(Itinerary.status, func.count(Itinerary.id)).group_by(Itinerary.status).all()
        total_for_status = sum(c[1] for c in status_counts) or 1
        formatted_status = [
            {"status": s[0].upper(), "count": s[1], "percentage": round((s[1]/total_for_status)*100, 1)}
            for s in status_counts
        ]

        # Monthly Revenue (Last 6 months) - Keep existing logic or optimize
        # For brevity, reusing the existing logic snippet for monthly
        monthly_data = []
        for i in range(5, -1, -1):
            month_start = (now.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            m_rev = db.query(func.sum(Itinerary.total_price)).filter(
                Itinerary.created_at >= month_start, Itinerary.created_at < next_month,
                Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
            ).scalar() or 0
            m_count = db.query(func.count(Itinerary.id)).filter(
                Itinerary.created_at >= month_start, Itinerary.created_at < next_month,
                Itinerary.status != ItineraryStatusEnum.DRAFT
            ).scalar() or 0
            monthly_data.append({"month": month_start.strftime("%b"), "revenue": float(m_rev), "bookings": m_count})

        return {
            "overview": {
                "totalRevenue": total_revenue,
                "revenueGrowth": round(revenue_growth, 1),
                "totalBookings": total_bookings,
                "bookingsGrowth": round(bookings_growth, 1),
                "activeCustomers": active_customers,
                "customersGrowth": 0.0,
                "avgBookingValue": round(avg_booking_val, 0),
                "avgBookingGrowth": 0.0
            },
            "monthlyRevenue": monthly_data,
            "bookingsByStatus": formatted_status,
            "paymentMetrics": {
                "totalPaid": total_paid,
                "totalPending": max(total_pending, 0),
                "totalDeposits": total_deposits,
                "avgPaymentTime": 0.0
            },
            
            # Admin Specifics
            "topDestinations": [
                {"destination": d['destination'], "bookings": d['count'], "revenue": 0.0}
                for d in company_analytics.get('popular_destinations', [])
            ],
            "topAgents": [
                {"name": a['agent'], "bookings": a['total_itineraries'], "revenue": 0, "conversion": a['completion_rate']}
                for a in company_analytics.get('agent_performance', [])
            ],
            "adminToday": admin_today['today'],
            "perAgentToday": admin_today['per_agent_today']
        }

    # ==================== AGENT VIEW ====================
    # ==================== AGENT VIEW ====================
    else:
        from app.models.permission import PermissionNames
        can_view_revenue = current_user.has_permission(PermissionNames.VIEW_ANALYTICS_REVENUE)

        # Get Agent Personal Stats
        agent_stats = analytics_service.get_agent_stats(current_user.id, db)
        agent_analytics = analytics_service.get_agent_analytics(current_user.id, date_from, date_to, db)

        # Overview (Personal)
        overview = agent_stats['overview']
        
        # Calculate revenue if permitted
        total_revenue = 0.0
        monthly_data = []
        
        if can_view_revenue:
            # Total Revenue
            total_revenue = db.query(func.sum(Itinerary.total_price)).filter(
                Itinerary.created_by_user_id == current_user.id,
                Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
            ).scalar() or 0.0
            
            # Monthly Revenue (Last 6 months)
            for i in range(5, -1, -1):
                month_start = (now.replace(day=1) - timedelta(days=30*i)).replace(day=1)
                next_month = (month_start + timedelta(days=32)).replace(day=1)
                m_rev = db.query(func.sum(Itinerary.total_price)).filter(
                    Itinerary.created_by_user_id == current_user.id,
                    Itinerary.created_at >= month_start, Itinerary.created_at < next_month,
                    Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
                ).scalar() or 0
                m_count = db.query(func.count(Itinerary.id)).filter(
                    Itinerary.created_by_user_id == current_user.id,
                    Itinerary.created_at >= month_start, Itinerary.created_at < next_month,
                    Itinerary.status != ItineraryStatusEnum.DRAFT
                ).scalar() or 0
                monthly_data.append({"month": month_start.strftime("%b"), "revenue": float(m_rev), "bookings": m_count})

        return {
            "overview": {
                "totalRevenue": float(total_revenue), 
                "revenueGrowth": 0,
                "totalBookings": overview['total_itineraries'],
                "bookingsGrowth": 0,
                "activeCustomers": 0,
                "customersGrowth": 0,
                "avgBookingValue": 0,
                "avgBookingGrowth": 0
            },
            "monthlyRevenue": monthly_data,
            "bookingsByStatus": [], # Could be personal status breakdown
            
            # Agent Specifics
            "agentToday": agent_stats['today'],
            "upcomingDepartures": agent_stats['upcoming_departures'],
            "recentActivity": agent_stats['recent_activity'],
            "agentOverview": overview
        }
