# MarkaMind Analytics Implementation - Analitik Uygulama Mimarisi

## 1. Genel Bakış

MarkaMind analytics sistemi, chatbot performansını, kullanıcı davranışlarını ve platform verimliliğini gerçek zamanlı olarak izlemek ve analiz etmek için tasarlanmıştır. Bu sistem, data-driven kararlar alabilmek için kapsamlı metrikler, dashboard'lar ve raporlama araçları sağlar.

### 1.1 Analytics Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                    Analytics Data Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Event     │ ─► │   Stream    │ ─► │   Real-time │         │
│  │ Generation  │    │ Processing  │    │ Dashboard   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Events    │    │   Redis     │    │  WebSocket  │         │
│  │ (Database)  │    │   Stream    │    │ Connections │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                                  │
│         ▼                   ▼                                  │
│  ┌─────────────┐    ┌─────────────┐                           │
│  │   Batch     │    │  ClickHouse │                           │
│  │ Processing  │    │  Analytics  │                           │
│  │  (Daily)    │    │   Engine    │                           │
│  └─────────────┘    └─────────────┘                           │
│         │                   │                                  │
│         ▼                   ▼                                  │
│  ┌─────────────────────────────────────────┐                  │
│  │           Reporting & Insights          │                  │
│  │     (Historical Analysis & ML)          │                  │
│  └─────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Gerçek Zamanlı Analiz Mimarisi

### 2.1 Event Streaming Architecture

#### Redis Streams Implementation
```python
# app/analytics/event_streaming.py
import redis
import json
from typing import Dict, Any, List
from datetime import datetime
from app.config.settings import settings

class EventStreamer:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.stream_keys = {
            "conversations": "stream:conversations",
            "messages": "stream:messages", 
            "user_actions": "stream:user_actions",
            "performance": "stream:performance",
            "errors": "stream:errors"
        }
    
    async def publish_event(self, stream_name: str, event_data: Dict[str, Any]):
        """Gerçek zamanlı event yayınlama"""
        try:
            event_payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"{stream_name}_{datetime.utcnow().timestamp()}",
                **event_data
            }
            
            # Redis Stream'e event ekleme
            stream_key = self.stream_keys.get(stream_name, f"stream:{stream_name}")
            message_id = self.redis_client.xadd(
                stream_key,
                event_payload,
                maxlen=10000  # Stream boyutunu sınırla
            )
            
            return message_id
            
        except Exception as e:
            logging.error(f"Event publishing failed: {e}")
            return None
    
    async def consume_events(self, stream_name: str, consumer_group: str, consumer_name: str):
        """Event stream'den veri okuma"""
        stream_key = self.stream_keys.get(stream_name)
        
        try:
            # Consumer group oluşturma (ilk kez)
            try:
                self.redis_client.xgroup_create(stream_key, consumer_group, id='0', mkstream=True)
            except redis.exceptions.ResponseError:
                pass  # Group zaten var
            
            while True:
                # Event'leri okuma
                messages = self.redis_client.xreadgroup(
                    consumer_group,
                    consumer_name,
                    {stream_key: '>'},
                    count=10,
                    block=1000
                )
                
                for stream, events in messages:
                    for message_id, fields in events:
                        yield message_id, fields
                        
                        # Message'ı acknowledge etme
                        self.redis_client.xack(stream_key, consumer_group, message_id)
                        
        except Exception as e:
            logging.error(f"Event consumption failed: {e}")
```

#### WebSocket Real-time Updates
```python
# app/analytics/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List, Set
import json

class AnalyticsWebSocketManager:
    def __init__(self):
        # Chatbot bazında WebSocket bağlantıları
        self.chatbot_connections: Dict[int, Set[WebSocket]] = {}
        # User bazında bağlantılar
        self.user_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect_to_chatbot(self, websocket: WebSocket, chatbot_id: int):
        """Chatbot analytics için bağlantı"""
        await websocket.accept()
        
        if chatbot_id not in self.chatbot_connections:
            self.chatbot_connections[chatbot_id] = set()
        
        self.chatbot_connections[chatbot_id].add(websocket)
    
    async def disconnect_from_chatbot(self, websocket: WebSocket, chatbot_id: int):
        """Chatbot bağlantısını sonlandırma"""
        if chatbot_id in self.chatbot_connections:
            self.chatbot_connections[chatbot_id].discard(websocket)
    
    async def broadcast_to_chatbot(self, chatbot_id: int, data: Dict):
        """Chatbot izleyicilerine gerçek zamanlı veri gönderme"""
        if chatbot_id in self.chatbot_connections:
            disconnected = set()
            
            for websocket in self.chatbot_connections[chatbot_id]:
                try:
                    await websocket.send_text(json.dumps(data))
                except:
                    disconnected.add(websocket)
            
            # Kopuk bağlantıları temizle
            for ws in disconnected:
                self.chatbot_connections[chatbot_id].discard(ws)
    
    async def broadcast_performance_update(self, chatbot_id: int, metrics: Dict):
        """Performance metriklerini gerçek zamanlı broadcast"""
        update_data = {
            "type": "performance_update",
            "chatbot_id": chatbot_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
        
        await self.broadcast_to_chatbot(chatbot_id, update_data)

# Global instance
websocket_manager = AnalyticsWebSocketManager()
```

### 2.2 Real-time Metrics Collector

#### Live Metrics Service
```python
# app/analytics/live_metrics.py
from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from app.analytics.event_streaming import EventStreamer

class LiveMetricsCollector:
    def __init__(self):
        self.event_streamer = EventStreamer()
        
        # In-memory cache for real-time metrics
        self.live_metrics = defaultdict(lambda: {
            "message_count": 0,
            "active_conversations": 0,
            "response_times": [],
            "error_count": 0,
            "satisfaction_scores": [],
            "last_updated": datetime.utcnow()
        })
    
    async def track_message_sent(self, chatbot_id: int, response_time_ms: int, confidence: float):
        """Mesaj gönderildiğinde metrik güncelleme"""
        # Live cache güncelleme
        self.live_metrics[chatbot_id]["message_count"] += 1
        self.live_metrics[chatbot_id]["response_times"].append(response_time_ms)
        self.live_metrics[chatbot_id]["last_updated"] = datetime.utcnow()
        
        # Response time window'u sınırlama (son 100 mesaj)
        if len(self.live_metrics[chatbot_id]["response_times"]) > 100:
            self.live_metrics[chatbot_id]["response_times"] = \
                self.live_metrics[chatbot_id]["response_times"][-100:]
        
        # Event stream'e publish
        await self.event_streamer.publish_event("messages", {
            "chatbot_id": chatbot_id,
            "event_type": "message_sent",
            "response_time_ms": response_time_ms,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # WebSocket üzerinden real-time güncelleme
        current_metrics = await self.get_live_metrics(chatbot_id)
        await websocket_manager.broadcast_performance_update(chatbot_id, current_metrics)
    
    async def track_conversation_started(self, chatbot_id: int, user_id: str):
        """Yeni conversation başladığında"""
        self.live_metrics[chatbot_id]["active_conversations"] += 1
        
        await self.event_streamer.publish_event("conversations", {
            "chatbot_id": chatbot_id,
            "event_type": "conversation_started",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def track_conversation_ended(self, chatbot_id: int, user_id: str, satisfaction_score: int = None):
        """Conversation sonlandığında"""
        self.live_metrics[chatbot_id]["active_conversations"] = max(0, 
            self.live_metrics[chatbot_id]["active_conversations"] - 1)
        
        if satisfaction_score:
            self.live_metrics[chatbot_id]["satisfaction_scores"].append(satisfaction_score)
            # Son 50 satisfaction score'u tut
            if len(self.live_metrics[chatbot_id]["satisfaction_scores"]) > 50:
                self.live_metrics[chatbot_id]["satisfaction_scores"] = \
                    self.live_metrics[chatbot_id]["satisfaction_scores"][-50:]
        
        await self.event_streamer.publish_event("conversations", {
            "chatbot_id": chatbot_id,
            "event_type": "conversation_ended",
            "user_id": user_id,
            "satisfaction_score": satisfaction_score,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def get_live_metrics(self, chatbot_id: int) -> Dict[str, Any]:
        """Chatbot için gerçek zamanlı metrikleri getirme"""
        metrics = self.live_metrics[chatbot_id].copy()
        
        # Hesaplanan metrikler
        if metrics["response_times"]:
            metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
            metrics["min_response_time"] = min(metrics["response_times"])
            metrics["max_response_time"] = max(metrics["response_times"])
        else:
            metrics["avg_response_time"] = 0
            metrics["min_response_time"] = 0
            metrics["max_response_time"] = 0
        
        if metrics["satisfaction_scores"]:
            metrics["avg_satisfaction"] = sum(metrics["satisfaction_scores"]) / len(metrics["satisfaction_scores"])
        else:
            metrics["avg_satisfaction"] = 0
        
        return metrics

# Global instance
live_metrics = LiveMetricsCollector()
```

## 3. Metrik Toplama Stratejileri

### 3.1 Event-Driven Metrics Collection

#### Core Events Definition
```python
# app/analytics/events.py
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

class EventType(Enum):
    # Conversation Events
    CONVERSATION_STARTED = "conversation_started"
    CONVERSATION_ENDED = "conversation_ended"
    CONVERSATION_ABANDONED = "conversation_abandoned"
    
    # Message Events  
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_FAILED = "message_failed"
    
    # User Actions
    USER_RATING = "user_rating"
    USER_FEEDBACK = "user_feedback"
    USER_CLICK = "user_click"
    
    # System Events
    CHATBOT_TRAINED = "chatbot_trained"
    CHATBOT_ACTIVATED = "chatbot_activated"
    CHATBOT_DEACTIVATED = "chatbot_deactivated"
    
    # Performance Events
    RESPONSE_TIME_HIGH = "response_time_high"
    ERROR_OCCURRED = "error_occurred"
    SYSTEM_HEALTH_CHECK = "system_health_check"

@dataclass
class AnalyticsEvent:
    event_type: EventType
    chatbot_id: int
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "chatbot_id": self.chatbot_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "data": self.data or {}
        }
```

#### Metrics Aggregation Service
```python
# app/analytics/metrics_aggregator.py
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.analytics import AnalyticsEvent, PerformanceMetric
from app.analytics.events import EventType

class MetricsAggregator:
    def __init__(self, db: Session):
        self.db = db
    
    async def aggregate_hourly_metrics(self, chatbot_id: int, hour: datetime) -> Dict:
        """Saatlik metrik toplama"""
        start_time = hour.replace(minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        # Event'leri veritabanından çekme
        events = self.db.query(AnalyticsEvent).filter(
            AnalyticsEvent.chatbot_id == chatbot_id,
            AnalyticsEvent.created_at >= start_time,
            AnalyticsEvent.created_at < end_time
        ).all()
        
        # Metrikleri hesaplama
        metrics = {
            "period_start": start_time.isoformat(),
            "period_end": end_time.isoformat(),
            "chatbot_id": chatbot_id,
            
            # Conversation metrics
            "conversations_started": len([e for e in events if e.event_type == EventType.CONVERSATION_STARTED.value]),
            "conversations_ended": len([e for e in events if e.event_type == EventType.CONVERSATION_ENDED.value]),
            "conversations_abandoned": len([e for e in events if e.event_type == EventType.CONVERSATION_ABANDONED.value]),
            
            # Message metrics
            "messages_sent": len([e for e in events if e.event_type == EventType.MESSAGE_SENT.value]),
            "messages_failed": len([e for e in events if e.event_type == EventType.MESSAGE_FAILED.value]),
            
            # Response time metrics
            "response_times": self._extract_response_times(events),
            
            # User satisfaction
            "user_ratings": self._extract_user_ratings(events),
            
            # Error metrics
            "error_count": len([e for e in events if e.event_type == EventType.ERROR_OCCURRED.value])
        }
        
        # Hesaplanan metrikler
        if metrics["response_times"]:
            metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
            metrics["p95_response_time"] = self._calculate_percentile(metrics["response_times"], 95)
        
        if metrics["user_ratings"]:
            metrics["avg_satisfaction"] = sum(metrics["user_ratings"]) / len(metrics["user_ratings"])
        
        # Conversion rates
        if metrics["conversations_started"] > 0:
            metrics["completion_rate"] = metrics["conversations_ended"] / metrics["conversations_started"]
            metrics["abandonment_rate"] = metrics["conversations_abandoned"] / metrics["conversations_started"]
        
        return metrics
    
    async def aggregate_daily_metrics(self, chatbot_id: int, date: datetime) -> Dict:
        """Günlük metrik toplama"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        # Saatlik metrikleri toplayarak günlük hesaplama
        hourly_metrics = []
        current_hour = start_date
        
        while current_hour < end_date:
            hour_metrics = await self.aggregate_hourly_metrics(chatbot_id, current_hour)
            hourly_metrics.append(hour_metrics)
            current_hour += timedelta(hours=1)
        
        # Günlük toplam hesaplama
        daily_metrics = {
            "date": date.date().isoformat(),
            "chatbot_id": chatbot_id,
            "total_conversations": sum(h["conversations_started"] for h in hourly_metrics),
            "total_messages": sum(h["messages_sent"] for h in hourly_metrics),
            "total_errors": sum(h["error_count"] for h in hourly_metrics),
            "peak_hour_conversations": max((h["conversations_started"] for h in hourly_metrics), default=0),
            "hourly_breakdown": hourly_metrics
        }
        
        return daily_metrics
    
    def _extract_response_times(self, events: List) -> List[float]:
        """Event'lerden response time'ları çıkarma"""
        response_times = []
        for event in events:
            if event.event_type == EventType.MESSAGE_SENT.value and event.event_data:
                if "response_time_ms" in event.event_data:
                    response_times.append(event.event_data["response_time_ms"])
        return response_times
    
    def _extract_user_ratings(self, events: List) -> List[int]:
        """Event'lerden user rating'leri çıkarma"""
        ratings = []
        for event in events:
            if event.event_type == EventType.USER_RATING.value and event.event_data:
                if "rating" in event.event_data:
                    ratings.append(event.event_data["rating"])
        return ratings
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Percentile hesaplama"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
```

### 3.2 Custom Metrics Definition

#### Business Metrics
```python
# app/analytics/business_metrics.py
from typing import Dict, List
from datetime import datetime, timedelta
from app.analytics.metrics_aggregator import MetricsAggregator

class BusinessMetricsCalculator:
    def __init__(self, aggregator: MetricsAggregator):
        self.aggregator = aggregator
    
    async def calculate_engagement_score(self, chatbot_id: int, period_days: int = 7) -> float:
        """Kullanıcı engagement skoru hesaplama"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Metrik toplama
        total_conversations = 0
        total_messages = 0
        total_unique_users = set()
        
        current_date = start_date
        while current_date < end_date:
            daily_metrics = await self.aggregator.aggregate_daily_metrics(chatbot_id, current_date)
            total_conversations += daily_metrics["total_conversations"]
            total_messages += daily_metrics["total_messages"]
            current_date += timedelta(days=1)
        
        # Engagement score hesaplama
        if total_conversations == 0:
            return 0.0
        
        avg_messages_per_conversation = total_messages / total_conversations
        engagement_score = min(avg_messages_per_conversation / 10, 1.0) * 100
        
        return round(engagement_score, 2)
    
    async def calculate_resolution_rate(self, chatbot_id: int, period_days: int = 7) -> float:
        """Problem çözüm oranı hesaplama"""
        # User feedback ve rating'ler üzerinden hesaplama
        # Rating >= 4 olan conversation'ları "resolved" olarak değerlendirme
        pass
    
    async def calculate_automation_rate(self, chatbot_id: int, period_days: int = 7) -> float:
        """Otomasyon oranı hesaplama"""
        # Human handover olmayan conversation'ların oranı
        pass
    
    async def calculate_cost_per_conversation(self, chatbot_id: int, period_days: int = 7) -> float:
        """Conversation başına maliyet hesaplama"""
        # API call maliyetleri, infrastructure costs vs.
        pass
```

## 4. Dashboard Veri Toplama

### 4.1 Dashboard Data Service

#### Real-time Dashboard API
```python
# app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.analytics.live_metrics import live_metrics
from app.analytics.websocket_manager import websocket_manager
from app.api.deps import get_current_user

router = APIRouter()

@router.websocket("/ws/chatbot/{chatbot_id}/metrics")
async def websocket_chatbot_metrics(
    websocket: WebSocket,
    chatbot_id: int,
    current_user = Depends(get_current_user)
):
    """Chatbot metrikleri için WebSocket bağlantısı"""
    try:
        await websocket_manager.connect_to_chatbot(websocket, chatbot_id)
        
        # İlk bağlantıda mevcut metrikleri gönder
        initial_metrics = await live_metrics.get_live_metrics(chatbot_id)
        await websocket.send_json({
            "type": "initial_metrics",
            "data": initial_metrics
        })
        
        # Bağlantıyı canlı tut
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect_from_chatbot(websocket, chatbot_id)

@router.get("/chatbot/{chatbot_id}/dashboard")
async def get_chatbot_dashboard(
    chatbot_id: int,
    period: str = "24h",
    current_user = Depends(get_current_user)
):
    """Chatbot dashboard verilerini getirme"""
    
    # Period parsing
    if period == "24h":
        hours = 24
    elif period == "7d":
        hours = 24 * 7
    elif period == "30d":
        hours = 24 * 30
    else:
        hours = 24
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Dashboard verileri toplama
    dashboard_data = {
        "chatbot_id": chatbot_id,
        "period": period,
        "generated_at": end_time.isoformat(),
        
        # Real-time metrics
        "live_metrics": await live_metrics.get_live_metrics(chatbot_id),
        
        # Historical metrics
        "historical_metrics": await get_historical_metrics(chatbot_id, start_time, end_time),
        
        # Performance trends
        "trends": await calculate_trends(chatbot_id, start_time, end_time),
        
        # User engagement
        "engagement": await calculate_engagement_metrics(chatbot_id, start_time, end_time),
        
        # Error analysis
        "errors": await get_error_analysis(chatbot_id, start_time, end_time)
    }
    
    return dashboard_data

async def get_historical_metrics(chatbot_id: int, start_time: datetime, end_time: datetime):
    """Geçmiş metrik verileri"""
    metrics = {
        "conversations": {
            "total": 0,
            "completed": 0,
            "abandoned": 0,
            "timeline": []
        },
        "messages": {
            "total": 0,
            "avg_per_conversation": 0,
            "timeline": []
        },
        "response_times": {
            "average": 0,
            "p50": 0,
            "p95": 0,
            "timeline": []
        },
        "satisfaction": {
            "average": 0,
            "distribution": [0, 0, 0, 0, 0],  # 1-5 star distribution
            "timeline": []
        }
    }
    
    # Veritabanından historical data çekme ve hesaplama
    # Implementation details...
    
    return metrics

async def calculate_trends(chatbot_id: int, start_time: datetime, end_time: datetime):
    """Trend hesaplamaları"""
    trends = {
        "conversation_growth": 0,  # %change
        "response_time_trend": 0,  # ms change
        "satisfaction_trend": 0,   # rating change
        "error_rate_trend": 0      # %change
    }
    
    # Trend calculation logic...
    
    return trends
```

#### Dashboard Widgets System
```python
# app/analytics/dashboard_widgets.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime, timedelta

class DashboardWidget(ABC):
    def __init__(self, widget_id: str, title: str):
        self.widget_id = widget_id
        self.title = title
    
    @abstractmethod
    async def get_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        pass

class ConversationVolumeWidget(DashboardWidget):
    def __init__(self):
        super().__init__("conversation_volume", "Conversation Volume")
    
    async def get_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        period = params.get("period", "24h")
        
        # Time series data for conversation volume
        data = {
            "widget_id": self.widget_id,
            "title": self.title,
            "chart_type": "line",
            "data": {
                "labels": [],  # Time labels
                "datasets": [{
                    "label": "Conversations",
                    "data": [],  # Conversation counts
                    "borderColor": "#3B82F6",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)"
                }]
            },
            "summary": {
                "total": 0,
                "change": 0,  # % change from previous period
                "trend": "up"  # up, down, stable
            }
        }
        
        # Data gathering logic...
        return data

class ResponseTimeWidget(DashboardWidget):
    def __init__(self):
        super().__init__("response_time", "Response Time Analysis")
    
    async def get_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        data = {
            "widget_id": self.widget_id,
            "title": self.title,
            "chart_type": "histogram",
            "data": {
                "labels": ["<500ms", "500ms-1s", "1s-2s", "2s-5s", ">5s"],
                "datasets": [{
                    "label": "Response Time Distribution",
                    "data": [0, 0, 0, 0, 0],
                    "backgroundColor": [
                        "#10B981", "#F59E0B", "#EF4444", "#DC2626", "#7F1D1D"
                    ]
                }]
            },
            "summary": {
                "average": 0,
                "p95": 0,
                "target": 1000  # Target response time in ms
            }
        }
        
        # Response time analysis logic...
        return data

class SatisfactionWidget(DashboardWidget):
    def __init__(self):
        super().__init__("satisfaction", "User Satisfaction")
    
    async def get_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        data = {
            "widget_id": self.widget_id,
            "title": self.title,
            "chart_type": "doughnut",
            "data": {
                "labels": ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"],
                "datasets": [{
                    "data": [0, 0, 0, 0, 0],
                    "backgroundColor": [
                        "#DC2626", "#F59E0B", "#6B7280", "#3B82F6", "#10B981"
                    ]
                }]
            },
            "summary": {
                "average": 0,
                "total_ratings": 0,
                "nps_score": 0  # Net Promoter Score
            }
        }
        
        # Satisfaction analysis logic...
        return data

class DashboardService:
    def __init__(self):
        self.widgets = {
            "conversation_volume": ConversationVolumeWidget(),
            "response_time": ResponseTimeWidget(),
            "satisfaction": SatisfactionWidget(),
            # Additional widgets...
        }
    
    async def get_dashboard_layout(self, user_id: int, chatbot_id: int) -> Dict:
        """Kullanıcı için dashboard layout'u"""
        # User preferences'a göre widget layout'u
        layout = {
            "rows": [
                {
                    "columns": [
                        {"widget": "conversation_volume", "span": 6},
                        {"widget": "response_time", "span": 6}
                    ]
                },
                {
                    "columns": [
                        {"widget": "satisfaction", "span": 4},
                        {"widget": "error_analysis", "span": 8}
                    ]
                }
            ]
        }
        
        return layout
    
    async def get_widget_data(self, widget_id: str, chatbot_id: int, params: Dict) -> Dict:
        """Belirli widget için veri getirme"""
        if widget_id in self.widgets:
            return await self.widgets[widget_id].get_data(chatbot_id, params)
        else:
            raise ValueError(f"Widget not found: {widget_id}")
```

### 4.2 Data Caching Strategy

#### Redis Cache Implementation
```python
# app/analytics/cache_manager.py
import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.config.settings import settings

class AnalyticsCacheManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.cache_prefixes = {
            "dashboard": "cache:dashboard:",
            "metrics": "cache:metrics:",
            "reports": "cache:reports:"
        }
    
    async def cache_dashboard_data(self, chatbot_id: int, period: str, data: Dict, ttl_seconds: int = 300):
        """Dashboard verilerini cache'leme (5 dakika TTL)"""
        cache_key = f"{self.cache_prefixes['dashboard']}{chatbot_id}:{period}"
        
        cached_data = {
            "data": data,
            "cached_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
        }
        
        self.redis_client.setex(
            cache_key,
            ttl_seconds,
            json.dumps(cached_data, default=str)
        )
    
    async def get_cached_dashboard_data(self, chatbot_id: int, period: str) -> Optional[Dict]:
        """Cache'den dashboard verilerini getirme"""
        cache_key = f"{self.cache_prefixes['dashboard']}{chatbot_id}:{period}"
        
        cached_json = self.redis_client.get(cache_key)
        if cached_json:
            cached_data = json.loads(cached_json)
            return cached_data["data"]
        
        return None
    
    async def invalidate_cache(self, chatbot_id: int, cache_type: str = "all"):
        """Cache'i temizleme"""
        if cache_type == "all":
            pattern = f"cache:*:{chatbot_id}:*"
        else:
            pattern = f"{self.cache_prefixes[cache_type]}{chatbot_id}:*"
        
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
```

## 5. Raporlama Sistemi Tasarımı

### 5.1 Report Generation Engine

#### Report Templates
```python
# app/analytics/report_templates.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template

class ReportTemplate(ABC):
    def __init__(self, template_id: str, name: str):
        self.template_id = template_id
        self.name = name
    
    @abstractmethod
    async def generate_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def render_report(self, data: Dict, format: str) -> bytes:
        pass

class PerformanceReportTemplate(ReportTemplate):
    def __init__(self):
        super().__init__("performance_report", "Performance Analysis Report")
    
    async def generate_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        
        data = {
            "report_id": f"perf_{chatbot_id}_{datetime.utcnow().strftime('%Y%m%d')}",
            "chatbot_id": chatbot_id,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "generated_at": datetime.utcnow().isoformat(),
            
            # Executive Summary
            "executive_summary": {
                "total_conversations": 0,
                "avg_response_time": 0,
                "user_satisfaction": 0,
                "error_rate": 0
            },
            
            # Detailed Metrics
            "metrics": {
                "conversation_analytics": {},
                "response_time_analysis": {},
                "user_engagement": {},
                "error_analysis": {}
            },
            
            # Trends and Insights
            "insights": [],
            
            # Recommendations
            "recommendations": []
        }
        
        # Data collection and analysis logic...
        return data
    
    async def render_report(self, data: Dict, format: str = "pdf") -> bytes:
        if format == "pdf":
            return await self._render_pdf(data)
        elif format == "html":
            return await self._render_html(data)
        elif format == "json":
            return json.dumps(data, indent=2, default=str).encode()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def _render_pdf(self, data: Dict) -> bytes:
        # PDF generation using reportlab or weasyprint
        # Chart generation with matplotlib
        # Template rendering with Jinja2
        pass
    
    async def _render_html(self, data: Dict) -> bytes:
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ data.report_id }} - Performance Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { border-bottom: 2px solid #333; padding-bottom: 20px; }
                .metric { margin: 20px 0; padding: 20px; border-left: 4px solid #007bff; }
                .chart { text-align: center; margin: 30px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Performance Analysis Report</h1>
                <p>Chatbot ID: {{ data.chatbot_id }}</p>
                <p>Period: {{ data.period.start }} - {{ data.period.end }}</p>
                <p>Generated: {{ data.generated_at }}</p>
            </div>
            
            <div class="executive-summary">
                <h2>Executive Summary</h2>
                <div class="metric">
                    <h3>Total Conversations: {{ data.executive_summary.total_conversations }}</h3>
                </div>
                <!-- Additional metrics... -->
            </div>
            
            <!-- Detailed sections... -->
        </body>
        </html>
        """
        
        template = Template(html_template)
        rendered_html = template.render(data=data)
        return rendered_html.encode()

class UserEngagementReportTemplate(ReportTemplate):
    def __init__(self):
        super().__init__("engagement_report", "User Engagement Analysis")
    
    async def generate_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        # User engagement specific data collection
        pass

class BusinessImpactReportTemplate(ReportTemplate):
    def __init__(self):
        super().__init__("business_impact", "Business Impact Report")
    
    async def generate_data(self, chatbot_id: int, params: Dict) -> Dict[str, Any]:
        # Business metrics and ROI analysis
        pass
```

#### Report Scheduler
```python
# app/analytics/report_scheduler.py
from celery import Celery
from datetime import datetime, timedelta
from app.analytics.report_templates import (
    PerformanceReportTemplate,
    UserEngagementReportTemplate,
    BusinessImpactReportTemplate
)
from app.services.email_service import EmailService

class ReportScheduler:
    def __init__(self):
        self.templates = {
            "performance": PerformanceReportTemplate(),
            "engagement": UserEngagementReportTemplate(),
            "business_impact": BusinessImpactReportTemplate()
        }
        self.email_service = EmailService()
    
    async def schedule_report(
        self, 
        chatbot_id: int, 
        template_id: str, 
        schedule: str,  # daily, weekly, monthly
        recipients: List[str],
        params: Dict = None
    ):
        """Rapor zamanlama"""
        job_params = {
            "chatbot_id": chatbot_id,
            "template_id": template_id,
            "recipients": recipients,
            "params": params or {}
        }
        
        if schedule == "daily":
            # Günlük 09:00'da çalışacak task
            generate_scheduled_report.apply_async(
                args=[job_params],
                eta=self._get_next_schedule_time("daily")
            )
        elif schedule == "weekly":
            # Haftalık pazartesi 09:00'da
            generate_scheduled_report.apply_async(
                args=[job_params],
                eta=self._get_next_schedule_time("weekly")
            )
        elif schedule == "monthly":
            # Aylık 1. gün 09:00'da
            generate_scheduled_report.apply_async(
                args=[job_params],
                eta=self._get_next_schedule_time("monthly")
            )
    
    def _get_next_schedule_time(self, schedule: str) -> datetime:
        now = datetime.utcnow()
        
        if schedule == "daily":
            next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif schedule == "weekly":
            # Next Monday at 9 AM
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=9, minute=0, second=0, microsecond=0)
        elif schedule == "monthly":
            # First day of next month
            if now.month == 12:
                next_run = now.replace(year=now.year+1, month=1, day=1, hour=9, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month+1, day=1, hour=9, minute=0, second=0, microsecond=0)
        
        return next_run

# Celery task
@celery_app.task
def generate_scheduled_report(job_params: Dict):
    """Zamanlanmış rapor oluşturma task'ı"""
    scheduler = ReportScheduler()
    
    chatbot_id = job_params["chatbot_id"]
    template_id = job_params["template_id"]
    recipients = job_params["recipients"]
    params = job_params["params"]
    
    # Default date range (last 7 days for weekly, last 30 days for monthly)
    end_date = datetime.utcnow()
    if template_id == "weekly":
        start_date = end_date - timedelta(days=7)
    elif template_id == "monthly":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=1)
    
    params.update({
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    })
    
    # Rapor oluşturma
    template = scheduler.templates[template_id]
    report_data = await template.generate_data(chatbot_id, params)
    report_content = await template.render_report(report_data, format="pdf")
    
    # Email gönderme
    await scheduler.email_service.send_report_email(
        recipients=recipients,
        subject=f"{template.name} - {datetime.utcnow().strftime('%Y-%m-%d')}",
        report_content=report_content,
        report_filename=f"{template_id}_{chatbot_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    )
```

### 5.2 Advanced Analytics

#### ML-Based Insights
```python
# app/analytics/ml_insights.py
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any

class MLInsightsGenerator:
    def __init__(self):
        pass
    
    async def detect_conversation_patterns(self, chatbot_id: int, days: int = 30) -> Dict[str, Any]:
        """Conversation pattern analizi"""
        # Son 30 günün conversation verileri
        conversations = await self._get_conversation_data(chatbot_id, days)
        
        if len(conversations) < 10:
            return {"error": "Insufficient data for pattern analysis"}
        
        # Feature engineering
        features = []
        for conv in conversations:
            features.append([
                conv["message_count"],
                conv["duration_minutes"],
                conv["hour_of_day"],
                conv["day_of_week"],
                conv["satisfaction_score"] or 0
            ])
        
        # Clustering
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(features_scaled)
        
        # Cluster analizi
        patterns = {}
        for i in range(3):
            cluster_convs = [conv for j, conv in enumerate(conversations) if clusters[j] == i]
            
            patterns[f"pattern_{i}"] = {
                "count": len(cluster_convs),
                "avg_messages": np.mean([c["message_count"] for c in cluster_convs]),
                "avg_duration": np.mean([c["duration_minutes"] for c in cluster_convs]),
                "avg_satisfaction": np.mean([c["satisfaction_score"] or 0 for c in cluster_convs]),
                "description": self._describe_pattern(cluster_convs)
            }
        
        return patterns
    
    async def predict_user_satisfaction(self, conversation_features: Dict) -> float:
        """User satisfaction prediction"""
        # Trained model ile satisfaction prediction
        # Features: response_time, message_count, conversation_length, etc.
        pass
    
    async def detect_anomalies(self, chatbot_id: int, hours: int = 24) -> List[Dict]:
        """Anomali tespiti"""
        # Son 24 saatlik metriklerde anomali detection
        # Statistical methods or ML-based approach
        pass
    
    def _describe_pattern(self, conversations: List[Dict]) -> str:
        """Pattern açıklaması oluşturma"""
        avg_messages = np.mean([c["message_count"] for c in conversations])
        avg_duration = np.mean([c["duration_minutes"] for c in conversations])
        
        if avg_messages < 3:
            return "Quick inquiries - Short conversations with minimal interaction"
        elif avg_messages > 10:
            return "Complex discussions - Extended conversations requiring detailed assistance"
        else:
            return "Standard interactions - Typical conversation flow with moderate engagement"
```

Bu analitik uygulama mimarisi şunları sağlıyor:

✅ **Gerçek Zamanlı İzleme**: Redis Streams ve WebSocket ile anlık metrik güncellemeleri
✅ **Kapsamlı Metrik Toplama**: Event-driven architecture ile detaylı veri toplama
✅ **İnteraktif Dashboard**: Modüler widget sistemi ile özelleştirilebilir dashboard'lar
✅ **Otomatik Raporlama**: Zamanlanmış rapor oluşturma ve email gönderimi
✅ **ML Tabanlı İçgörüler**: Pattern analizi ve anomali tespiti
✅ **Performans Optimizasyonu**: Redis cache ile hızlı veri erişimi
✅ **Ölçeklenebilir Mimari**: Celery background tasks ile asenkron işleme

Bu sistem, MarkaMind platformunda chatbot performansını optimize etmek ve kullanıcı deneyimini sürekli iyileştirmek için gerekli tüm analitik yetenekleri sağlar.