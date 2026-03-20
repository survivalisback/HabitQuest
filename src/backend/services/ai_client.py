import json
import logging
import re

logger = logging.getLogger(__name__)


class AiClient:
    def __init__(self, api_key: str, model: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def evaluate_habit_xp(
        self,
        name: str,
        description: str,
        frequency: str,
        difficulty: int,
        static_xp: int,
    ) -> int | None:
        prompt = (
            f"You are an XP evaluator for a gamified habit tracker.\n"
            f"Evaluate this habit and return a fair XP reward.\n\n"
            f"Habit: {name}\n"
            f"Description: {description or 'N/A'}\n"
            f"Frequency: {frequency}\n"
            f"Difficulty: {difficulty}/5\n"
            f"Static baseline XP: {static_xp}\n\n"
            f"Consider the effort, impact, and consistency required.\n"
            f"Return ONLY valid JSON: {{\"xp\": <integer>, \"reasoning\": \"<short explanation>\"}}\n"
            f"The XP must be between {int(static_xp * 0.5)} and {int(static_xp * 2.0)}."
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            data = self._parse_json_response(text)
            xp = int(data["xp"])
            # Clamp to allowed range
            lower = int(static_xp * 0.5)
            upper = int(static_xp * 2.0)
            return max(lower, min(upper, xp))
        except Exception as e:
            logger.warning("AI XP evaluation failed: %s", e)
            return None

    @staticmethod
    def _parse_json_response(text: str) -> dict:
        # First try direct parse for strict JSON output.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Handle fenced markdown output like ```json ... ```.
        fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, flags=re.IGNORECASE)
        if fenced:
            return json.loads(fenced.group(1))

        # Last resort: extract the first JSON object block.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])

        raise json.JSONDecodeError("No JSON object found in AI response.", text, 0)
