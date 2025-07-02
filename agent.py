from dotenv import load_dotenv
import os
# from .api_proto import ClientEvents, LiveAPIModels, Voice
# from .realtime_api import RealtimeModel
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation

load_dotenv()

# Debug: Check if environment variables are loaded
print(f"GOOGLE_API_KEY loaded: {os.getenv('GOOGLE_API_KEY') is not None}")
print(f"GOOGLE_API_KEY value: {os.getenv('GOOGLE_API_KEY', 'NOT_FOUND')[:20]}...")  # Show first 20 chars


class Assistant(Agent):
    def __init__(self) -> None:
        healthcare_instructions = """You are a professional AI receptionist for SmileCare Dental Practice.

Your main tasks:
- Book appointments and answer scheduling questions
- Provide basic information about services and office hours
- Collect patient contact details when booking
- NEVER give medical advice or diagnose conditions
- For emergencies, direct patients to call 911
- Be warm, professional, and helpful

Office hours: Monday-Saturday 9:00 AM to 5:00 PM
Appointment types: Cleaning (30min), Consultation (30min), Emergency (30min)"""

        super().__init__(instructions=healthcare_instructions)


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
    llm=google.beta.realtime.RealtimeModel(
        model="gemini-2.0-flash-exp",
        voice="Puck",
        temperature=0.5,
        instructions="You are a friendly healthcare receptionist. Help patients with appointments and basic questions.",
    ),
)

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=""""Greet the patient professionally with: 
        "Hello! Thank you for calling SmileCare Dental Practice. I'm your AI assistant Sarah. 
        How may I help you today? I can help you schedule appointments, answer questions about our services, 
        or connect you with our medical staff if needed." 
        
        Be warm and professional."""
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))


