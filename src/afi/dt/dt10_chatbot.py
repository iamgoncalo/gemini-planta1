import os
import json
from datetime import datetime, timezone

class HORSE_CFT_SpaceBot:
    """
    DT-10: Conversational AI interface for HORSE CFT Digital Twin.
    Grounded in real-time AFI data. Never fabricates building values.
    """

    SYSTEM_PROMPT_TEMPLATE = """
You are PlantaOS Space Intelligence — the AI brain of the HORSE CFT building
(Centro de Formação Técnica, Cacia, Aveiro, Portugal).

You have access to real-time sensor data and AFI Freedom Index scores.
NEVER make up sensor values. ALWAYS reference the current data snapshot.
If a room is not in the snapshot, say so explicitly.

## Current Building State ({timestamp})

F_global = {F_global:.3f}  |  Occupancy: {total_occupancy}/{max_occupancy} persons

### Room Status (F = Freedom Index, P = Perception, D = Distortion):
{room_status_table}

### Alerts:
{alerts}

## Your Capabilities
- Explain what is happening in any room or the whole building
- Predict what will happen in the next 1–4 hours (based on LBM model)
- Suggest specific actions to improve Freedom (comfort, energy, air quality)
- Answer questions about energy consumption, occupancy, and training schedules
- Check the training calendar and warn about upcoming events

## How you answer
- Always cite specific room names, F values, and timestamps
- Never say "I think" or "maybe" about sensor data — it is measured
- For predictions: say "LBM predicts..." and give confidence
- Keep answers concise — this is an operational interface, not a report
"""

    def __init__(self, use_free_model=True):
        self.use_litellm = use_free_model
        self.conversation_history = []

    def chat(self, user_message: str, building_state: dict) -> str:
        system_prompt = self._build_system_prompt(building_state)

        self.conversation_history.append({
            "role": "user", "content": user_message
        })

        try:
            if self.use_litellm:
                import litellm
                # Uses Gemini 1.5 Flash via LiteLLM if GEMINI_API_KEY is set
                response = litellm.completion(
                    model="gemini/gemini-2.0-flash",
                    messages=[{"role": "system", "content": system_prompt}] + self.conversation_history,
                    max_tokens=800,
                )
                reply = response.choices[0].message.content
            else:
                import anthropic
                client = anthropic.Anthropic() # Expects ANTHROPIC_API_KEY env var
                response = client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=800,
                    system=system_prompt,
                    messages=self.conversation_history,
                )
                reply = response.content[0].text
        except Exception as e:
            reply = f"[API Error] Please ensure your API keys are exported in the terminal. Details: {str(e)}"

        self.conversation_history.append({
            "role": "assistant", "content": reply
        })
        return reply

    def _build_system_prompt(self, state: dict) -> str:
        rows = []
        for room, vals in state.get("F_by_room", {}).items():
            F, P, D = vals.get("F", 0.0), vals.get("P", 0.0), vals.get("D", 0.0)
            occ = state.get("occupancy", {}).get(room, 0)
            flag = "⚠️ LOW" if F < 0.50 else ("⬇" if F < 0.70 else "✓")
            rows.append(f"  {room}: F={F:.2f} P={P:.1f} D={D:.1f} Occ={occ} {flag}")

        alert_str = "\n".join(f"  [ALERT] {a}" for a in state.get("alerts", [])) or "  None"

        return self.SYSTEM_PROMPT_TEMPLATE.format(
            timestamp=state.get("timestamp", datetime.now(timezone.utc).isoformat()),
            F_global=state.get("F_global", 0.0),
            total_occupancy=sum(state.get("occupancy", {}).values()),
            max_occupancy=320,
            room_status_table="\n".join(rows),
            alerts=alert_str,
        )

if __name__ == "__main__":
    print("--- DT-10 SpaceBot Initialization ---")
    
    # Mocking the state exactly as calculated in our previous steps
    mock_building_state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "F_global": 0.68,
        "occupancy": {"Sala_Multiusos": 5, "Auditorio": 59, "Sala_A": 12},
        "F_by_room": {
            "Sala_Multiusos": {"F": 0.85, "P": 4.5, "D": 5.3},
            "Auditorio": {"F": 0.35, "P": 6.2, "D": 17.7}, # Danger zone!
            "Sala_A": {"F": 0.80, "P": 4.1, "D": 5.1}
        },
        "alerts": ["Auditorio: COMBINED_FAILURE (Crowd/Complex) - High CO2 and Crowding detected."]
    }

    bot = HORSE_CFT_SpaceBot(use_free_model=True)
    
    print("\nSimulating User Query: 'What is the current status of the Auditorio? How can we fix it?'")
    
    # Check if API keys exist before making the call to prevent terminal crashes
    if os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        response = bot.chat("What is the current status of the Auditorio? How can we fix it?", mock_building_state)
        print(f"\nPlantaOS Bot:\n{response}")
    else:
        print("\n[Notice] API Keys not detected. To see the AI response, run:")
        print("export GEMINI_API_KEY='your_key' (or ANTHROPIC_API_KEY)")
        print("python src/afi/dt/dt10_chatbot.py")
