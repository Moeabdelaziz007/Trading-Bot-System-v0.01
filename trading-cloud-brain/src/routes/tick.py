"""
⏱️ UNIFIED TICK ENDPOINT - Manual Brain Heartbeat Trigger
Allows triggering the cron logic via HTTP for:
1. Testing without waiting for scheduled cron
2. Frontend "Force Refresh" button
3. Debugging agent behavior

Endpoint: POST /api/tick
"""

from js import Response
import json
import datetime

# Import from cron module
from routes.cron import on_scheduled


async def handle_tick(request, env, headers):
    """
    Manual trigger for the AlphaAxiom brain heartbeat.
    
    POST /api/tick
    Body (optional): { "fast_only": true } - Only run fast agents
    
    Returns:
        JSON with tick result and timing info
    """
    start_time = datetime.datetime.utcnow()
    
    try:
        # Parse optional body
        try:
            body = await request.json()
        except:
            body = {}
        
        fast_only = body.get("fast_only", False)
        
        # Create a mock event object (since we're not in actual cron context)
        class MockEvent:
            pass
        
        mock_event = MockEvent()
        
        # Run the scheduled handler
        if fast_only:
            # Just update heartbeat and run fast agents
            kv = env.BRAIN_MEMORY
            await kv.put("swarm_heartbeat", start_time.isoformat())
            await kv.put("tick_source", "manual_api")
            
            result = {
                "status": "partial",
                "agents": ["heartbeat"],
                "fast_only": True
            }
        else:
            # Run full cron logic
            await on_scheduled(mock_event, env)
            
            result = {
                "status": "complete",
                "agents": ["risk", "heartbeat", "fast", "15min", "hourly", "learning"],
                "fast_only": False
            }
        
        end_time = datetime.datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        return Response.new(json.dumps({
            "success": True,
            "tick": result,
            "timing": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_ms": round(duration_ms, 2)
            }
        }), headers=headers)
        
    except Exception as e:
        return Response.new(json.dumps({
            "success": False,
            "error": str(e)
        }), status=500, headers=headers)


async def get_brain_status(env, headers):
    """
    GET /api/brain/status
    Returns the current state of the AlphaAxiom brain.
    """
    try:
        kv = env.BRAIN_MEMORY
        
        # Fetch all brain state
        heartbeat = await kv.get("swarm_heartbeat")
        mode = await kv.get("swarm_mode")
        panic = await kv.get("panic_mode")
        panic_reason = await kv.get("panic_reason")
        aexi = await kv.get("aexi_score")
        dream = await kv.get("dream_score")
        last_signal = await kv.get("last_signal")
        tick_source = await kv.get("tick_source")
        
        # Calculate time since last heartbeat
        if heartbeat:
            try:
                last_beat = datetime.datetime.fromisoformat(heartbeat.replace('Z', '+00:00'))
                now = datetime.datetime.utcnow()
                seconds_ago = (now - last_beat.replace(tzinfo=None)).total_seconds()
                health = "healthy" if seconds_ago < 120 else "stale" if seconds_ago < 300 else "dead"
            except:
                seconds_ago = None
                health = "unknown"
        else:
            seconds_ago = None
            health = "never_started"
        
        return Response.new(json.dumps({
            "brain_status": health,
            "heartbeat": {
                "last": heartbeat,
                "seconds_ago": round(seconds_ago, 1) if seconds_ago else None,
                "source": tick_source or "scheduled"
            },
            "mode": mode or "SIMULATION",
            "panic": {
                "active": panic == "true",
                "reason": panic_reason
            },
            "engines": {
                "aexi": float(aexi) if aexi else 50.0,
                "dream": float(dream) if dream else 50.0
            },
            "last_signal": json.loads(last_signal) if last_signal else None
        }), headers=headers)
        
    except Exception as e:
        return Response.new(json.dumps({
            "brain_status": "error",
            "error": str(e)
        }), status=500, headers=headers)
