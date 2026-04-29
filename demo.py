"""
demo.py
───────
Standalone demo — NO Telegram token needed.
Tests the NLP parser with Arabic & English samples.

Run: python demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# ── Minimal stub so demo works without installing all deps ───────────────────
try:
    import dateparser
except ImportError:
    print("⚠️  Run: pip install dateparser\n")
    sys.exit(1)

from nlp.parser import ReminderParser

SAMPLES = [
    # Arabic samples
    "ذكرني بموعد الطبيب الأحد المقبل الساعة 9 مساءً",
    "ذكرني بدفع الإيجار غداً الساعة 10 صباحاً",
    "ذكرني باجتماع الفريق الخميس الساعة 2 مساءً",
    # English samples
    "Remind me to call the dentist next Monday at 11 AM",
    "Remind me about the team meeting tomorrow at 3:30 PM",
    # Edge case
    "مرحبا كيف حالك",  # No date — should fail gracefully
]

parser = ReminderParser()

print("=" * 60)
print("  🤖 Telegram Reminder Bot — NLP Parser Demo")
print("=" * 60)

for text in SAMPLES:
    result = parser.parse(text)
    print(f"\n📨 Input   : {text}")
    print(f"   Title   : {result.title}")

    if result.is_parsed:
        dt_str = result.datetime_obj.strftime("%A, %d %B %Y — %I:%M %p")
        print(f"   DateTime: {dt_str}")
        print(f"   Timestamp: {int(result.datetime_obj.timestamp())}")
        print(f"   Confidence: {int(result.confidence * 100)}%  ✅")
    else:
        print("   DateTime: ❌ Could not parse date from this message")

print("\n" + "=" * 60)
print("  Demo complete. Wire main.py to your Telegram bot token.")
print("=" * 60)
