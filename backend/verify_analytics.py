import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import func

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app.db.session import SessionLocal
    from app.models.itinerary import Itinerary, ItineraryStatusEnum, PaymentStatusEnum, Traveler
    from app.models.user import User
    from app.schemas.analytics import AnalyticsResponse
    
    db = SessionLocal()
    print("Database connection successful.")
except Exception as e:
    print(f"Setup failed: {e}")
    sys.exit(1)

def check_analytics():
    print("Running analytics logic...")
    try:
        now = datetime.utcnow()
        last_month = now - timedelta(days=30)
        
        # 1. Overview Metrics
        # Total Revenue
        total_revenue_dec = db.query(func.sum(Itinerary.total_price)).filter(
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
        ).scalar() or 0
        total_revenue = float(total_revenue_dec)
        
        # Previous Period Revenue
        prev_revenue_dec = db.query(func.sum(Itinerary.total_price)).filter(
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED]),
            Itinerary.created_at < last_month
        ).scalar() or 0
        prev_revenue = float(prev_revenue_dec)

        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0.0

        # Total Bookings
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
        
        # Avg Booking Value
        avg_booking_val = (total_revenue / total_bookings) if total_bookings > 0 else 0.0
        
        # 2. Monthly Revenue (Last 6 months)
        monthly_data = []
        for i in range(5, -1, -1):
            month_start = (now.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            
            m_rev = db.query(func.sum(Itinerary.total_price)).filter(
                Itinerary.created_at >= month_start,
                Itinerary.created_at < next_month,
                Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
            ).scalar() or 0
            
            m_count = db.query(func.count(Itinerary.id)).filter(
                Itinerary.created_at >= month_start,
                Itinerary.created_at < next_month,
                Itinerary.status != ItineraryStatusEnum.DRAFT
            ).scalar() or 0
            
            monthly_data.append({
                "month": month_start.strftime("%b"),
                "revenue": float(m_rev),
                "bookings": m_count
            })

        # 3. Top Destinations
        top_destinations = db.query(
            Itinerary.tour_title.label('destination'),
            func.count(Itinerary.id).label('count'),
            func.sum(Itinerary.total_price).label('revenue')
        ).filter(
            Itinerary.status != ItineraryStatusEnum.DRAFT
        ).group_by(Itinerary.tour_title).order_by(func.count(Itinerary.id).desc()).limit(5).all()
        
        formatted_destinations = [
            {"destination": r.destination, "bookings": r.count, "revenue": float(r.revenue or 0)} 
            for r in top_destinations
        ]

        # 4. Agent Performance
        top_agents_query = db.query(
            User.full_name,
            func.count(Itinerary.id).label('bookings'),
            func.sum(Itinerary.total_price).label('revenue')
        ).join(Itinerary, User.id == Itinerary.assigned_to_user_id).filter(
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
        ).group_by(User.full_name).limit(5).all()
        
        formatted_agents = [
            {"name": r.full_name, "bookings": r.bookings, "revenue": float(r.revenue or 0), "conversion": 0.0}
            for r in top_agents_query
        ]

        # 5. Booking Status
        status_counts = db.query(
            Itinerary.status,
            func.count(Itinerary.id)
        ).group_by(Itinerary.status).all()
        
        total_for_status = sum(c[1] for c in status_counts) or 1
        formatted_status = [
            {"status": s[0].upper(), "count": s[1], "percentage": round((s[1]/total_for_status)*100, 1)}
            for s in status_counts
        ]

        # 6. Payment Metrics
        total_paid_dec = db.query(func.sum(Itinerary.deposit_amount)).filter(
            Itinerary.payment_status == PaymentStatusEnum.FULLY_PAID
        ).scalar() or 0
        total_paid = float(total_paid_dec)
        
        total_deposits_dec = db.query(func.sum(Itinerary.deposit_amount)).filter(
            Itinerary.payment_status == PaymentStatusEnum.PARTIALLY_PAID
        ).scalar() or 0
        total_deposits = float(total_deposits_dec)
        
        total_pending = total_revenue - (total_paid + total_deposits)

        # Construct response dict
        response_data = {
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
            "topDestinations": formatted_destinations,
            "topAgents": formatted_agents,
            "bookingsByStatus": formatted_status,
            "paymentMetrics": {
                "totalPaid": total_paid,
                "totalPending": total_pending if total_pending > 0 else 0.0,
                "totalDeposits": total_deposits,
                "avgPaymentTime": 0.0
            }
        }
        
        print("Validating against schema...")
        validated = AnalyticsResponse(**response_data)
        print("Schema validation successful!")
        # print(validated.json(indent=2)) 
        
    except Exception as e:
        print(f"❌ Error during analytics execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_analytics()
