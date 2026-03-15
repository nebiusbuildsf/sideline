"""Tool definitions for the Sideline referee agent."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "update_score",
            "description": "Update the game score after a point is won",
            "parameters": {
                "type": "object",
                "properties": {
                    "player": {
                        "type": "string",
                        "enum": ["p1", "p2"],
                        "description": "Which player won the point",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why the point was awarded (ace, winner, double fault, unforced error, etc.)",
                    },
                },
                "required": ["player", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "announce_call",
            "description": "Announce a referee call out loud",
            "parameters": {
                "type": "object",
                "properties": {
                    "call_type": {
                        "type": "string",
                        "enum": [
                            "fault",
                            "out",
                            "in",
                            "let",
                            "ace",
                            "winner",
                            "double_fault",
                            "no_call",
                        ],
                    },
                    "announcement": {
                        "type": "string",
                        "description": "What to say (e.g. 'Fault! Second serve.')",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "0-1 confidence in the call",
                    },
                },
                "required": ["call_type", "announcement"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "robot_gesture",
            "description": "Signal the call with a physical robot gesture",
            "parameters": {
                "type": "object",
                "properties": {
                    "gesture": {
                        "type": "string",
                        "enum": [
                            "point_out",
                            "arm_up",
                            "wave_off",
                            "hold",
                            "signal_fault",
                            "idle",
                        ],
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["left", "right", "center"],
                    },
                },
                "required": ["gesture"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "no_call",
            "description": "No scoring event occurred. Rally is ongoing or nothing notable happened.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Brief note (e.g. 'Rally continues, baseline exchange')",
                    }
                },
                "required": ["description"],
            },
        },
    },
]
