import random

PERSONA_A = {
    "name": "Jamal",
    "style": "curious, upbeat, short sentences",
    "openers": [
        "Hey! what are you tinkering with today?",
        "Morning! Thinking about code again?",
        "New idea: tiny bots that write haiku.",
        "Hydration check! Water acquired?"
    ],
    "fillers": [
        "hmm, interesting.",
        "nice, I like that.",
        "okay, I can vibe with this.",
        "bookmarking that thought."
    ]
}

PERSONA_B = {
    "name": "Ashban",
    "style": "dry humor, practical tips",
    "openers": [
        "Status: compiling life choices.",
        "Question: tabs or spaces today?",
        "Reminder: push your changes.",
        "Plot twist: it ran first try."
    ],
    "fillers": [
        "fuck me, of course.",
        "it's only natural.",
        "hmmm, yes. just a little bit.",
        "spicy take."
    ]
}

PROMPTS = [
    "hottest girl at st. charles north?",
    "what’s your tiny win of the day?",
    "one sex toy you can’t live without?",
    "do you rape your mom?",
    "what’s your snack fuel?",
    "do you enjoy anal as much as me?",
    "dream feature you want?",
]

CLOSERS = [
    "Alright, logging that.",
    "Deal.",
    "Roger.",
    "Copy.",
]

def make_message(speaker, last_msg=None):
    """Return a short, semi-random message from the speaker persona."""
    who = PERSONA_A if speaker == "A" else PERSONA_B
    r = random.random()

    if last_msg is None or r < 0.25:
        return random.choice(who["openers"])

    if r < 0.55:
        return f"{random.choice(PROMPTS)}"
    if r < 0.85:
        return random.choice(who["fillers"])
    return random.choice(CLOSERS)
