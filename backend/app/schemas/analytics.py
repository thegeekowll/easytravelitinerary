from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import date

# ==================== Common ====================
class OverviewMetrics(BaseModel):
    totalRevenue: float
    revenueGrowth: float
    totalBookings: int
    bookingsGrowth: float
    activeCustomers: int
    customersGrowth: float
    avgBookingValue: float
    avgBookingGrowth: float

class MonthlyRevenue(BaseModel):
    month: str
    revenue: float
    bookings: int

class TopDestination(BaseModel):
    destination: str
    bookings: int
    revenue: float

class BookingStatusDistribution(BaseModel):
    status: str
    count: int
    percentage: float

class PaymentMetrics(BaseModel):
    totalPaid: float
    totalPending: float
    totalDeposits: float
    avgPaymentTime: float

# ==================== Admin Specific ====================

class TopAgent(BaseModel):
    name: str
    bookings: int
    revenue: float
    conversion: float

class AdminTodayStats(BaseModel):
    total_itineraries_created: int
    total_emails_sent: int
    active_agents: int
    departures_today: int

class AgentActivityToday(BaseModel):
    agent: str
    itineraries_created: int

# ==================== Agent Specific ====================

class AgentTodayStats(BaseModel):
    itineraries_created: int
    itineraries_edited: int
    emails_sent: int
    departures_today: int

class UpcomingDeparture(BaseModel):
    id: str
    title: str
    departure_date: str
    days_until: int
    traveler: str

class RecentActivityItem(BaseModel):
    action: str
    description: str
    timestamp: str
    entity_id: Optional[str] = None
    entity_type: str

class AgentOverview(BaseModel):
    total_itineraries: int
    incomplete_count: int
    complete_count: int

# ==================== Main Response ====================

class AnalyticsResponse(BaseModel):
    # Common / Shared (Admin sees total, Agent sees personal)
    overview: OverviewMetrics  
    monthlyRevenue: List[MonthlyRevenue]
    bookingsByStatus: List[BookingStatusDistribution]
    paymentMetrics: Optional[PaymentMetrics] = None # Admin only usually

    # Admin Specific
    topDestinations: Optional[List[TopDestination]] = None
    topAgents: Optional[List[TopAgent]] = None
    
    adminToday: Optional[AdminTodayStats] = None
    perAgentToday: Optional[List[AgentActivityToday]] = None

    # Agent Specific
    agentToday: Optional[AgentTodayStats] = None
    upcomingDepartures: Optional[List[UpcomingDeparture]] = None
    recentActivity: Optional[List[RecentActivityItem]] = None
    agentOverview: Optional[AgentOverview] = None
