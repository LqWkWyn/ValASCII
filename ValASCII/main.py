#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ValASCII - Valorant Friend Monitor & ASCII Art Spammer
Uses Riot Client local API (lockfile-based)
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import base64
import json
import requests
import urllib3
from pathlib import Path
try:
    import winsound as _winsound
    def _beep():
        _winsound.MessageBeep(_winsound.MB_ICONEXCLAMATION)
except ImportError:
    def _beep():
        pass  # non-Windows: no sound
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Theme ──────────────────────────────────────────────────────────────────────
BG_DARK       = "#0d0d14"
BG_PANEL      = "#13131f"
BG_CARD       = "#1a1a2e"
BG_INPUT      = "#0f0f1a"
BG_HOVER      = "#1f2245"
BG_SEL        = "#2a2f5a"
ACCENT        = "#FF4655"
ACCENT_DIM    = "#cc3344"
TEXT_MAIN     = "#ece8e1"
TEXT_DIM      = "#8a8fa8"
TEXT_ONLINE   = "#3fa757"
TEXT_AWAY     = "#e8ac30"
TEXT_DND      = "#e84040"
TEXT_OFFLINE  = "#4a4f60"
BORDER        = "#252540"

LOCKFILE = Path(os.environ.get("LOCALAPPDATA", "")) / \
           "Riot Games" / "Riot Client" / "Config" / "lockfile"

POLL_INTERVAL = 5  # seconds

# ── Store constants ────────────────────────────────────────────────────────────
VP_ID         = "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"
RADIANITE_ID  = "e59aa87c-4cbf-517a-5983-6e81511be9b7"
KC_ID         = "85ca954a-41f2-ce94-9b45-8ca3dd39a00d"
# Standard base64 PC client platform string accepted by Riot's remote API
CLIENT_PLATFORM = (
    "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0K"
    "CSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxh"
    "dGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
)

SHARD_MAP = {
    "na": "na", "pbe": "na", "latam": "na", "br": "na",
    "eu": "eu",
    "ap": "ap",
    "kr": "kr",
}

def _region_to_shard(region: str) -> str:
    """
    Map a region string to its PD shard.  Riot returns variants like
    'eu1', 'eu2', 'na1', 'ap1' etc. — strip trailing digits then look up.
    """
    region = region.lower().strip()
    if region in SHARD_MAP:
        return SHARD_MAP[region]
    base = region.rstrip("0123456789")
    return SHARD_MAP.get(base, "na")

# ── ASCII Art Library (valoranttextart.com) ────────────────────────────────────
ASCII_ART = {
    "Gorilla / Monkey": (
        "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        "⣿⣿⣿⡿⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢿⣿⣿⣿⣿\n"
        "⣿⣿⡟⠁⠀⠀⣠⣶⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠹⣿⣿⣿\n"
        "⣿⡟⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⢻⣿⣿\n"
        "⣿⠁⠀⠀⣾⣿⣿⣿⡿⠿⠛⠛⠿⢿⣿⣿⣿⣇⠀⠀⠀⠀⠈⣿⣿\n"
        "⡏⠀⠀⢸⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⡄⠀⠀⠀⠀⢻⣿\n"
        "⠁⠀⠀⣿⣿⡟⠀⠀⣠⡄⠀⠀⣠⡄⠀⠀⢻⣿⣿⠀⠀⠀⠀⠈⣿\n"
        "⠀⠀⢸⣿⣿⠀⠀⠀⠛⠃⠀⠀⠛⠃⠀⠀⠀⣿⣿⡄⠀⠀⠀⠀⢹\n"
        "⠀⠀⣾⣿⣿⠀⠀⠀⠀⣀⣤⣤⣀⠀⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀\n"
        "⠀⢸⣿⣿⣿⠀⠀⠀⢸⣿⣿⣿⣿⡇⠀⠀⠀⣿⣿⣇⠀⠀⠀⠀⠀\n"
        "⠀⣿⣿⣿⡏⠀⠀⠀⢸⣿⣿⣿⣿⡇⠀⠀⠀⢸⣿⣿⠀⠀⠀⠀⠀\n"
        "⢸⣿⣿⣿⠀⠀⠀⠀⠀⠙⠛⠛⠋⠀⠀⠀⠀⠀⣿⣿⡆⠀⠀⠀⠀\n"
        "⣿⣿⣿⣿⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣿⣿⣿⣤⣤⣤⡄\n"
        "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿"
    ),
    "Nerd": (
        "⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⢀⣾⣿⣿⣿⡆⠀⠀⢰⣿⣿⣿⣷⡀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⢸⣿⣉⣉⣿⡇⠀⠀⢸⣿⣉⣉⣿⡇⠀⠀⠀⠀\n"
        "⠀⠀⠀⢀⣸⣿⣿⣿⣿⣧⡀⢀⣼⣿⣿⣿⣿⣇⡀⠀⠀⠀\n"
        "⠀⣠⡾⠛⠋⠀⠀⠀⠀⠈⠛⠛⠁⠀⠀⠀⠀⠙⠛⢷⣄⠀\n"
        "⣸⡿⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⢿⣧\n"
        "⣿⡇⠀⠀⠀⠀⠀⠀⣠⡀⠀⢀⣄⠀⠀⠀⠀⠀⠀⠀⢸⣿\n"
        "⣿⡇⠀⠀⠀⠀⠀⠀⠉⠁⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⢸⣿\n"
        "⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿\n"
        "⠹⣿⣿⣶⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣴⣿⣿⣿⠟\n"
        "⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀\n"
        "⠀⠀⠀⠀⠉⠉⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⠉⠀⠀⠀⠀"
    ),
    "Among Us": (
        "⠀⠀⣠⣾⣿⣿⣿⣷⣄⠀\n"
        "⠀⣼⣿⣿⣿⣿⣿⣿⣿⣧\n"
        "⠀⣿⣿⠛⣿⣿⣿⠛⣿⣿\n"
        "⠀⣿⣿⠀⣿⣿⣿⠀⣿⣿\n"
        "⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        "⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        "⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        "⣀⣿⣿⣿⣿⣿⣿⣿⣿⣀\n"
        "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        "⠈⣿⣿⠁⣿⣿⠁⣿⣿⠁"
    ),
    "GG EZ": (
        " ██████╗  ██████╗     ███████╗███████╗\n"
        "██╔════╝ ██╔════╝     ██╔════╝╚══███╔╝\n"
        "██║  ███╗██║  ███╗    █████╗    ███╔╝ \n"
        "██║   ██║██║   ██║    ██╔══╝   ███╔╝  \n"
        "╚██████╔╝╚██████╔╝    ███████╗███████╗\n"
        " ╚═════╝  ╚═════╝     ╚══════╝╚══════╝"
    ),
    "Delete Valo!": (
        "██████╗ ███████╗██╗     ███████╗████████╗███████╗\n"
        "██╔══██╗██╔════╝██║     ██╔════╝╚══██╔══╝██╔════╝\n"
        "██║  ██║█████╗  ██║     █████╗     ██║   █████╗  \n"
        "██║  ██║██╔══╝  ██║     ██╔══╝     ██║   ██╔══╝  \n"
        "██████╔╝███████╗███████╗███████╗   ██║   ███████╗\n"
        "╚═════╝ ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚══════╝\n"
        "██╗   ██╗ █████╗ ██╗      ██████╗ ██╗\n"
        "██║   ██║██╔══██╗██║     ██╔═══██╗██║\n"
        "██║   ██║███████║██║     ██║   ██║██║\n"
        "╚██╗ ██╔╝██╔══██║██║     ██║   ██║╚═╝\n"
        " ╚████╔╝ ██║  ██║███████╗╚██████╔╝██╗\n"
        "  ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝"
    ),
    "Noob": (
        "███╗   ██╗ ██████╗  ██████╗ ██████╗ \n"
        "████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗\n"
        "██╔██╗ ██║██║   ██║██║   ██║██████╔╝\n"
        "██║╚██╗██║██║   ██║██║   ██║██╔══██╗\n"
        "██║ ╚████║╚██████╔╝╚██████╔╝██████╔╝\n"
        "╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ "
    ),
    "VALORANT": (
        "██╗   ██╗ █████╗ ██╗      ██████╗ ██████╗  █████╗ ███╗   ██╗████████╗\n"
        "██║   ██║██╔══██╗██║     ██╔═══██╗██╔══██╗██╔══██╗████╗  ██║╚══██╔══╝\n"
        "██║   ██║███████║██║     ██║   ██║██████╔╝███████║██╔██╗ ██║   ██║   \n"
        "╚██╗ ██╔╝██╔══██║██║     ██║   ██║██╔══██╗██╔══██║██║╚██╗██║   ██║   \n"
        " ╚████╔╝ ██║  ██║███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚████║   ██║   \n"
        "  ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝  "
    ),
    "Copium": (
        "⠀⠀⣰⣷⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣆⠀\n"
        "⠀⠸⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⠇⠀\n"
        "⠀⠀⠘⢿⣿⣿⣿⣿⣦⣀⣴⣿⣿⣿⣿⡿⠃⠀⠀\n"
        "⠀⠀⢠⣄⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣠⡄⠀\n"
        "⠀⣴⣿⣿⣿⣦⡙⢿⣿⣿⣿⣿⡿⢋⣴⣿⣿⣿⣦\n"
        "⢠⣿⣿⣿⣿⣿⣿⣦⡙⢿⣿⠟⢁⣼⣿⣿⣿⣿⣿\n"
        "⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⢹⢿⣿⣿⣿⣿⣿⣿⣿\n"
        "⠻⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⢀⣴⣾⣿⣿⣿⣿⠟\n"
        "⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⠃⠸⣿⣿⣿⣿⣿⠋⠀\n"
        "⠀⠀⠀⢀⣹⡿⠿⢿⣿⡏⠀⢸⣿⡿⠿⣿⣦⡀⠀\n"
        "⠀⠀⠀⠈⠉⠁⠀⠙⠛⠁⠀⠈⠛⠋⠀⠈⠉⠁⠀"
    ),
    "Middle Finger": (
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⢰⣶⠀⢰⣶⠀⢸⣿⡇⠀⢰⣶⠀⠀⢰⣶⠀\n"
        "⠀⠀⢸⣿⠀⢸⣿⠀⢸⣿⡇⠀⢸⣿⠀⠀⢸⣿⠀\n"
        "⠀⠀⢸⣿⠀⢸⣿⠀⢸⣿⡇⠀⢸⣿⠀⠀⢸⣿⠀\n"
        "⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀\n"
        "⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀\n"
        "⠀⠀⠀⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠀"
    ),
    "Duolingo (Do ur lessons)": (
        "⠀⠀⠀⠀⠀⣠⣴⣶⣦⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⣠⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀\n"
        "⠀⠀⢸⣿⣿⡛⣿⡟⢿⣿⠀⠀⠀⠀⠀\n"
        "⠀⠀⠘⣿⣿⣄⣿⡇⣼⣿⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠈⠻⠿⣿⣿⠿⠋⠀⠀⠀⠀⠀\n"
        "⠀⣤⣤⣤⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠻⣿⡿⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⣿⡇⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀\n"
        "⠀⠘⠛⠛⠛⠛⠛⠛⠛⠛⠛⠀⠀⠀⠀\n"
        "DO YOUR LESSONS OR ELSE."
    ),
}


# ── JWT helper ────────────────────────────────────────────────────────────────

def _decode_jwt(token: str) -> dict:
    """Decode a JWT payload section without verifying the signature."""
    try:
        payload_b64 = token.split('.')[1]
        payload_b64 += '=' * (-len(payload_b64) % 4)
        return json.loads(base64.b64decode(payload_b64))
    except Exception:
        return {}


def resolve_skin_name(level_uuid: str) -> str:
    """
    Look up a skin name by the exact level UUID Riot's store returns.
    Uses the per-UUID endpoint so there is no bulk-cache mismatch risk.
    Falls back to the skins list endpoint if the level endpoint 404s.
    """
    # Primary: direct level UUID lookup
    try:
        r = requests.get(
            f"https://valorant-api.com/v1/weapons/skinlevels/{level_uuid}",
            timeout=10,
        )
        if r.ok:
            name = r.json().get("data", {}).get("displayName", "")
            if name:
                return name
    except Exception:
        pass

    # Fallback: search the full skins list
    try:
        r = requests.get("https://valorant-api.com/v1/weapons/skins", timeout=15)
        if r.ok:
            for skin in r.json().get("data", []):
                if skin.get("uuid") == level_uuid:
                    return skin["displayName"]
                for level in skin.get("levels", []):
                    if level.get("uuid") == level_uuid:
                        return skin["displayName"]
    except Exception:
        pass

    return f"Unknown skin"


# ── Lockfile / API ─────────────────────────────────────────────────────────────

class LockfileError(Exception):
    pass


def read_lockfile() -> tuple[int, str]:
    if not LOCKFILE.exists():
        raise LockfileError(
            f"Lockfile not found.\nMake sure Riot Client is running.\n\n{LOCKFILE}"
        )
    text = LOCKFILE.read_text()
    parts = text.strip().split(":")
    # name:pid:port:password:protocol
    _, _, port, password, _ = parts
    return int(port), password


class RiotAPI:
    def __init__(self, port: int, password: str):
        self.port = port
        self.base = f"https://127.0.0.1:{port}"
        self._session = requests.Session()
        self._session.verify = False
        creds = base64.b64encode(f"riot:{password}".encode()).decode()
        self._session.headers["Authorization"] = f"Basic {creds}"
        self._session.headers["Content-Type"] = "application/json"

    def get_friends(self) -> list:
        r = self._session.get(f"{self.base}/chat/v4/friends")
        r.raise_for_status()
        return r.json().get("friends", [])

    def get_presences(self) -> dict:
        r = self._session.get(f"{self.base}/chat/v4/presences")
        r.raise_for_status()
        return {p["puuid"]: p for p in r.json().get("presences", [])}

    def get_conversations(self) -> list:
        r = self._session.get(f"{self.base}/chat/v6/conversations")
        r.raise_for_status()
        return r.json().get("conversations", [])

    def get_messages(self, cid: str) -> list:
        r = self._session.get(f"{self.base}/chat/v6/messages", params={"cid": cid})
        r.raise_for_status()
        return r.json().get("messages", [])

    def send_message(self, cid: str, message: str) -> dict:
        payload = {"cid": cid, "message": message, "type": "chat"}
        r = self._session.post(f"{self.base}/chat/v6/messages", json=payload)
        r.raise_for_status()
        return r.json()

    def get_chat_session(self) -> dict:
        """
        /chat/v1/session is the ground-truth source for the account that is
        actively logged into the Riot Chat system (i.e. actually playing).
        Returns fields: puuid, game_name, game_tag, name, region.
        """
        r = self._session.get(f"{self.base}/chat/v1/session")
        r.raise_for_status()
        return r.json()

    def _try_product_auth(self, correct_puuid: str) -> Optional[dict]:
        """
        When /entitlements/v1/token has stale tokens for a different account,
        try the Riot Client's product-specific RSO auth endpoints to obtain
        tokens whose JWT subject matches correct_puuid.

        Returns {access_token, entitlement_token} or None.
        """
        # Client IDs the Riot Client may expose product-specific tokens under
        for client_id in ("valorant-game", "valorant", "riot_client_auth", "riot_client"):
            try:
                r = self._session.get(
                    f"{self.base}/rso-auth/v2/authorizations/{client_id}"
                )
                if not r.ok:
                    continue
                d = r.json()
                # Response shape varies by client — flatten the common locations
                access_token = (
                    d.get("accessToken")
                    or d.get("access_token")
                    or (d.get("authorization") or {}).get("accessToken", {}).get("token")
                    or (d.get("token") or {}).get("access_token")
                )
                if not access_token:
                    continue

                # Only use this token if its sub actually matches the game account
                if _decode_jwt(access_token).get("sub") != correct_puuid:
                    continue

                # Fetch a fresh entitlement JWT that is bound to this access token
                ent_r = requests.post(
                    "https://entitlements.auth.riotgames.com/api/token/v1",
                    headers={
                        "Authorization":  f"Bearer {access_token}",
                        "Content-Type":   "application/json",
                    },
                    json={},
                    timeout=10,
                )
                if ent_r.ok:
                    ent_token = ent_r.json().get("entitlements_token", "")
                    if ent_token:
                        return {"access_token": access_token,
                                "entitlement_token": ent_token}
            except Exception:
                continue
        return None

    def get_auth_info(self) -> dict:
        """
        Return {access_token, entitlement_token, puuid, display_name} for
        the account that is *actually* logged into Valorant right now.

        Flow:
          1. puuid  ← /chat/v1/session          (tied to the live game session)
          2. tokens ← /entitlements/v1/token    (fast path)
          3. Decode the access-token JWT; if its sub == puuid we're done.
          4. sub mismatch → the cached tokens belong to a different account.
             Try /rso-auth/v2/authorizations/* for a Valorant-specific token,
             then re-issue an entitlement JWT via the remote endpoint.
          5. If everything fails, raise with a clear message.
        """
        chat         = self.get_chat_session()
        correct_puuid = chat.get("puuid", "")
        display_name  = f"{chat.get('game_name','')}#{chat.get('game_tag','')}"

        ent_r = self._session.get(f"{self.base}/entitlements/v1/token")
        ent_r.raise_for_status()
        ent = ent_r.json()

        access_token      = ent["accessToken"]
        entitlement_token = ent["token"]
        ent_subject       = ent.get("subject", "")          # field Riot provides directly
        token_sub         = _decode_jwt(access_token).get("sub", "") or ent_subject

        # Fast path: token belongs to the logged-in account
        if token_sub == correct_puuid:
            return {
                "access_token":      access_token,
                "entitlement_token": entitlement_token,
                "puuid":             correct_puuid or ent.get("subject", ""),
                "display_name":      display_name,
            }

        # Slow path: cached tokens are for a DIFFERENT account – try product auth
        product = self._try_product_auth(correct_puuid)
        if product:
            return {
                "access_token":      product["access_token"],
                "entitlement_token": product["entitlement_token"],
                "puuid":             correct_puuid,
                "display_name":      display_name,
            }

        # Nothing worked – raise a clear, actionable error
        raise RuntimeError(
            f"Auth token mismatch.\n\n"
            f"The Riot Client's cached token belongs to a different account "
            f"(sub: …{token_sub[-8:]}) than the one playing Valorant "
            f"(puuid: …{correct_puuid[-8:]}).\n\n"
            "Fix: close ALL Riot Client windows, reopen, and log in with only "
            "your main account before launching ValASCII."
        )

    def get_region(self) -> tuple[str, str]:
        """
        Return (region, shard).  /chat/v1/session is primary because it
        is tied to the active game session; falls back to region-locale.
        """
        try:
            chat   = self.get_chat_session()
            region = chat.get("region", "").lower()
            if region:
                return region, _region_to_shard(region)
        except Exception:
            pass
        r      = self._session.get(f"{self.base}/riotclient/region-locale")
        r.raise_for_status()
        region = r.json().get("region", "na").lower()
        return region, _region_to_shard(region)

    def get_shop(self) -> dict:
        """
        Fetch the daily store offers.  Returns a dict with:
          'offers'  – list of {name, vp_cost} dicts (4 items on a normal day)
          'vp'      – int VP balance
          'rad'     – int Radianite balance
          'kc'      – int Kingdom Credits balance
        Raises on any network or auth error.
        """
        auth = self.get_auth_info()
        region, shard = self.get_region()

        ver_r = requests.get("https://valorant-api.com/v1/version", timeout=10)
        ver_r.raise_for_status()
        client_version = ver_r.json()["data"]["riotClientVersion"]

        remote_headers = {
            "X-Riot-ClientPlatform":   CLIENT_PLATFORM,
            "X-Riot-ClientVersion":    client_version,
            "X-Riot-Entitlements-JWT": auth["entitlement_token"],
            "Authorization":           f"Bearer {auth['access_token']}",
            "Content-Type":            "application/json",
        }
        pd_url = f"https://pd.{shard}.a.pvp.net"
        puuid  = auth["puuid"]

        shop_r = requests.post(
            f"{pd_url}/store/v3/storefront/{puuid}",
            headers=remote_headers,
            json={},
            timeout=15,
        )
        shop_r.raise_for_status()
        shop_data = shop_r.json()

        wallet_r = requests.get(
            f"{pd_url}/store/v1/wallet/{puuid}",
            headers=remote_headers,
            timeout=10,
        )
        wallet_r.raise_for_status()
        wallet_raw = wallet_r.json()

        # Case-insensitive lookup for Balances key
        balances = {}
        for k, v in wallet_raw.items():
            if k.lower() == "balances":
                balances = v
                break

        panel        = shop_data.get("SkinsPanelLayout", {})
        level_uuids  = panel.get("SingleItemOffers", [])
        store_offers = panel.get("SingleItemStoreOffers", [])

        # Build uuid→VP-cost map from the detailed offers list
        price_map: dict[str, int] = {}
        for o in store_offers:
            rewards = o.get("Rewards") or [{}]
            iid     = rewards[0].get("ItemID", "")
            price_map[iid] = o.get("Cost", {}).get(VP_ID, 0)

        # If the plain UUID list is empty, fall back to extracting from detailed offers
        if not level_uuids:
            level_uuids = list(price_map.keys())

        offers = []
        for uuid in level_uuids:
            if not uuid:
                continue
            name    = resolve_skin_name(uuid)
            vp_cost = price_map.get(uuid, 0)
            offers.append({"name": name, "vp_cost": vp_cost, "item_id": uuid})

        return {
            "offers":        offers,
            "vp":            balances.get(VP_ID, 0),
            "rad":           balances.get(RADIANITE_ID, 0),
            "kc":            balances.get(KC_ID, 0),
            "display_name":  auth.get("display_name", ""),
        }

    def find_dm_cid(self, friend_pid: str) -> str:
        """Return existing DM conversation ID or fall back to friend's pid."""
        try:
            convos = self.get_conversations()
            for c in convos:
                if c.get("type") == "chat" and friend_pid in c.get("cid", ""):
                    return c["cid"]
        except Exception:
            pass
        return friend_pid


# ── Toast notification ─────────────────────────────────────────────────────────

def show_toast(root: tk.Tk, name: str, tag: str):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.attributes("-alpha", 0.0)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    w, h = 300, 72
    x = screen_w - w - 18
    y = screen_h - h - 56
    toast.geometry(f"{w}x{h}+{x}+{y}")
    toast.configure(bg=BORDER)

    inner = tk.Frame(toast, bg=BG_CARD, padx=12, pady=8)
    inner.pack(fill="both", expand=True, padx=1, pady=1)

    top_row = tk.Frame(inner, bg=BG_CARD)
    top_row.pack(fill="x")
    tk.Label(top_row, text="●", bg=BG_CARD, fg=TEXT_ONLINE,
             font=("Segoe UI", 10)).pack(side="left")
    tk.Label(top_row, text="  Friend Online", bg=BG_CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Label(inner, text=f"{name}#{tag} is now online",
             bg=BG_CARD, fg=TEXT_MAIN, font=("Segoe UI", 9)).pack(anchor="w")

    def fade_in(alpha=0.0):
        alpha = min(alpha + 0.08, 0.95)
        toast.attributes("-alpha", alpha)
        if alpha < 0.95:
            toast.after(20, lambda: fade_in(alpha))

    def fade_out(alpha=0.95):
        alpha = max(alpha - 0.06, 0.0)
        toast.attributes("-alpha", alpha)
        if alpha > 0:
            toast.after(25, lambda: fade_out(alpha))
        else:
            toast.destroy()

    fade_in()
    _beep()
    toast.after(4000, lambda: fade_out())


# ── Main Application ───────────────────────────────────────────────────────────

class ValASCII(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ValASCII")
        self.configure(bg=BG_DARK)
        self.geometry("900x640")
        self.minsize(760, 520)

        self.api: Optional[RiotAPI] = None
        self._friends: list = []
        self._presences: dict = {}
        self._prev_online: set = set()
        self._selected_pid: Optional[str] = None
        self._selected_cid: Optional[str] = None
        self._spam_thread: Optional[threading.Thread] = None
        self._spam_stop = threading.Event()
        self._poll_thread: Optional[threading.Thread] = None
        self._running = True

        self._build_ui()
        self._try_connect()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar ────────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=BG_PANEL, height=46)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        tk.Label(top, text="VAL", bg=BG_PANEL, fg=ACCENT,
                 font=("Consolas", 15, "bold")).pack(side="left", padx=(14, 0), pady=8)
        tk.Label(top, text="ASCII", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=("Consolas", 15, "bold")).pack(side="left", pady=8)

        self._status_dot = tk.Label(top, text="●", bg=BG_PANEL, fg=TEXT_OFFLINE,
                                    font=("Segoe UI", 11))
        self._status_dot.pack(side="right", padx=(0, 8))
        self._status_lbl = tk.Label(top, text="Disconnected", bg=BG_PANEL,
                                    fg=TEXT_DIM, font=("Segoe UI", 9))
        self._status_lbl.pack(side="right", padx=(0, 4))

        tk.Button(top, text="⟳ Reconnect", bg=BG_CARD, fg=TEXT_MAIN,
                  activebackground=BG_HOVER, activeforeground=TEXT_MAIN,
                  relief="flat", cursor="hand2", padx=10,
                  command=self._try_connect).pack(side="right", padx=(0, 14), pady=8)

        tk.Button(top, text="🛒 SHOP", bg=ACCENT, fg="white",
                  activebackground=ACCENT_DIM, activeforeground="white",
                  relief="flat", cursor="hand2", padx=12,
                  font=("Consolas", 9, "bold"),
                  command=self._open_shop).pack(side="right", padx=(0, 6), pady=8)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x")

        # ── Main pane ──────────────────────────────────────────────────────────
        pane = tk.PanedWindow(self, orient="horizontal", bg=BG_DARK,
                              sashrelief="flat", sashwidth=4, sashpad=0)
        pane.pack(fill="both", expand=True)

        # ── Left: Friend list ──────────────────────────────────────────────────
        left = tk.Frame(pane, bg=BG_PANEL, width=220)
        left.pack_propagate(False)
        pane.add(left, minsize=180)

        hdr = tk.Frame(left, bg=BG_PANEL)
        hdr.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(hdr, text="FRIENDS", bg=BG_PANEL, fg=TEXT_DIM,
                 font=("Consolas", 8, "bold")).pack(side="left")
        self._online_count = tk.Label(hdr, text="0 online", bg=BG_PANEL,
                                      fg=ACCENT, font=("Consolas", 8))
        self._online_count.pack(side="right")

        list_frame = tk.Frame(left, bg=BG_PANEL)
        list_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        sb = tk.Scrollbar(list_frame, bg=BG_PANEL, troughcolor=BG_PANEL,
                          relief="flat", bd=0)
        sb.pack(side="right", fill="y")

        self._friends_lb = tk.Listbox(
            list_frame,
            bg=BG_PANEL, fg=TEXT_MAIN,
            selectbackground=BG_SEL, selectforeground=TEXT_MAIN,
            activestyle="none",
            relief="flat", bd=0,
            font=("Segoe UI", 9),
            yscrollcommand=sb.set,
            highlightthickness=0,
        )
        self._friends_lb.pack(fill="both", expand=True)
        sb.config(command=self._friends_lb.yview)
        self._friends_lb.bind("<<ListboxSelect>>", self._on_friend_select)

        # ── Right panel ────────────────────────────────────────────────────────
        right = tk.Frame(pane, bg=BG_DARK)
        pane.add(right, minsize=480)

        # Chat area (top ~60%)
        chat_outer = tk.Frame(right, bg=BG_DARK)
        chat_outer.pack(fill="both", expand=True)

        chat_hdr = tk.Frame(chat_outer, bg=BG_PANEL, height=36)
        chat_hdr.pack(fill="x")
        chat_hdr.pack_propagate(False)
        self._recipient_lbl = tk.Label(chat_hdr, text="Select a friend →",
                                       bg=BG_PANEL, fg=TEXT_DIM,
                                       font=("Segoe UI", 9, "italic"))
        self._recipient_lbl.pack(side="left", padx=12, pady=8)

        tk.Frame(chat_outer, bg=BORDER, height=1).pack(fill="x")

        self._chat_text = tk.Text(
            chat_outer,
            bg=BG_INPUT, fg=TEXT_MAIN,
            font=("Consolas", 9),
            relief="flat", bd=0,
            state="disabled",
            wrap="word",
            highlightthickness=0,
            padx=10, pady=8,
        )
        self._chat_text.pack(fill="both", expand=True)
        self._chat_text.tag_config("you",    foreground=ACCENT)
        self._chat_text.tag_config("them",   foreground="#6fc3df")
        self._chat_text.tag_config("time",   foreground=TEXT_DIM)
        self._chat_text.tag_config("system", foreground=TEXT_DIM,
                                   font=("Consolas", 8, "italic"))

        # Input bar
        input_bar = tk.Frame(chat_outer, bg=BG_PANEL, height=46)
        input_bar.pack(fill="x")
        input_bar.pack_propagate(False)

        self._msg_var = tk.StringVar()
        self._msg_entry = tk.Entry(
            input_bar,
            textvariable=self._msg_var,
            bg=BG_INPUT, fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            relief="flat", bd=0,
            font=("Segoe UI", 10),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._msg_entry.pack(side="left", fill="both", expand=True, padx=(10, 6), pady=8)
        self._msg_entry.bind("<Return>", lambda _: self._send_message())
        self._msg_entry.bind("<KP_Enter>", lambda _: self._send_message())

        tk.Button(
            input_bar, text="SEND",
            bg=ACCENT, fg="white",
            activebackground=ACCENT_DIM, activeforeground="white",
            relief="flat", cursor="hand2",
            font=("Consolas", 9, "bold"), padx=14,
            command=self._send_message,
        ).pack(side="right", padx=(0, 10), pady=8)

        # ── ASCII Art panel (bottom) ───────────────────────────────────────────
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")

        ascii_panel = tk.Frame(right, bg=BG_PANEL)
        ascii_panel.pack(fill="x", side="bottom")

        art_top = tk.Frame(ascii_panel, bg=BG_PANEL)
        art_top.pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(art_top, text="ASCII ART", bg=BG_PANEL, fg=TEXT_DIM,
                 font=("Consolas", 8, "bold")).pack(side="left")
        tk.Label(art_top, text="valoranttextart.com", bg=BG_PANEL, fg=TEXT_OFFLINE,
                 font=("Consolas", 7)).pack(side="right")

        art_row = tk.Frame(ascii_panel, bg=BG_PANEL)
        art_row.pack(fill="x", padx=10, pady=(0, 4))

        self._art_var = tk.StringVar(value=list(ASCII_ART.keys())[0])
        art_combo = ttk.Combobox(
            art_row,
            textvariable=self._art_var,
            values=list(ASCII_ART.keys()),
            state="readonly",
            font=("Segoe UI", 9),
            width=28,
        )
        art_combo.pack(side="left")
        art_combo.bind("<<ComboboxSelected>>", self._on_art_select)

        tk.Frame(art_row, bg=BG_PANEL, width=10).pack(side="left")

        tk.Label(art_row, text="×", bg=BG_PANEL, fg=TEXT_DIM,
                 font=("Segoe UI", 10)).pack(side="left")
        self._count_var = tk.StringVar(value="5")
        count_entry = tk.Entry(
            art_row,
            textvariable=self._count_var,
            bg=BG_INPUT, fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            relief="flat", bd=0,
            font=("Consolas", 10),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            width=4,
            justify="center",
        )
        count_entry.pack(side="left", padx=(4, 8), ipady=3)

        self._art_btn = tk.Button(
            art_row, text="⚡ SPAM ART",
            bg=ACCENT, fg="white",
            activebackground=ACCENT_DIM, activeforeground="white",
            relief="flat", cursor="hand2",
            font=("Consolas", 9, "bold"), padx=12,
            command=self._toggle_spam,
        )
        self._art_btn.pack(side="left")

        self._spam_status = tk.Label(art_row, text="", bg=BG_PANEL, fg=TEXT_DIM,
                                     font=("Consolas", 8))
        self._spam_status.pack(side="left", padx=(10, 0))

        # Art preview
        preview_frame = tk.Frame(ascii_panel, bg=BG_INPUT,
                                 highlightthickness=1,
                                 highlightbackground=BORDER)
        preview_frame.pack(fill="x", padx=10, pady=(0, 8))

        self._art_preview = tk.Text(
            preview_frame,
            bg=BG_INPUT, fg=TEXT_MAIN,
            font=("Consolas", 7),
            relief="flat", bd=0,
            height=8,
            state="disabled",
            wrap="none",
            highlightthickness=0,
            padx=8, pady=4,
        )
        self._art_preview.pack(fill="x")

        self._style_combobox()
        self._update_art_preview()

    def _style_combobox(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=BG_INPUT,
                        background=BG_CARD,
                        foreground=TEXT_MAIN,
                        selectbackground=BG_SEL,
                        selectforeground=TEXT_MAIN,
                        bordercolor=BORDER,
                        arrowcolor=TEXT_DIM,
                        padding=(6, 4))
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG_INPUT)],
                  foreground=[("readonly", TEXT_MAIN)])
        self.option_add("*TCombobox*Listbox.background", BG_CARD)
        self.option_add("*TCombobox*Listbox.foreground", TEXT_MAIN)
        self.option_add("*TCombobox*Listbox.selectBackground", BG_SEL)
        self.option_add("*TCombobox*Listbox.selectForeground", TEXT_MAIN)

    # ── Connection ─────────────────────────────────────────────────────────────

    def _try_connect(self):
        try:
            port, password = read_lockfile()
            self.api = RiotAPI(port, password)
            self._set_status(True)
            self._start_poll()
        except LockfileError as e:
            self.api = None
            self._set_status(False)
            self._chat_append(f"⚠  {e}", tag="system")

    def _set_status(self, connected: bool):
        if connected:
            self._status_dot.config(fg=TEXT_ONLINE)
            self._status_lbl.config(text="Connected")
        else:
            self._status_dot.config(fg=TEXT_OFFLINE)
            self._status_lbl.config(text="Disconnected")

    # ── Polling ────────────────────────────────────────────────────────────────

    def _start_poll(self):
        if self._poll_thread and self._poll_thread.is_alive():
            return
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    def _poll_loop(self):
        while self._running and self.api:
            try:
                friends   = self.api.get_friends()
                presences = self.api.get_presences()
                self.after(0, lambda f=friends, p=presences: self._update_friends(f, p))
            except Exception as e:
                self.after(0, lambda: self._set_status(False))
            time.sleep(POLL_INTERVAL)

    def _update_friends(self, friends: list, presences: dict):
        self._friends   = friends
        self._presences = presences

        now_online = set()
        for f in friends:
            p = presences.get(f["puuid"], {})
            state = p.get("state", "")
            if state in ("chat", "mobile"):
                now_online.add(f["puuid"])

        # Alert for newly online friends
        newly = now_online - self._prev_online
        for puuid in newly:
            f = next((x for x in friends if x["puuid"] == puuid), None)
            if f:
                show_toast(self, f["game_name"], f.get("game_tag", ""))

        self._prev_online = now_online

        # Sort: online first, then alphabetically
        def sort_key(f):
            p   = presences.get(f["puuid"], {})
            st  = p.get("state", "")
            ord = {"chat": 0, "mobile": 1, "away": 2, "dnd": 3}.get(st, 4)
            return (ord, f["game_name"].lower())

        sorted_friends = sorted(friends, key=sort_key)

        self._friends_lb.delete(0, "end")
        self._friend_order = sorted_friends  # keep reference for click lookup

        online_n = sum(1 for f in friends if presences.get(f["puuid"], {}).get("state") in ("chat", "mobile"))
        self._online_count.config(text=f"{online_n} online")

        for f in sorted_friends:
            p     = presences.get(f["puuid"], {})
            state = p.get("state", "")
            dot   = {"chat": "● ", "mobile": "◉ ", "away": "● ", "dnd": "⊗ "}.get(state, "○ ")
            name  = f"{f['game_name']}#{f.get('game_tag','')}"
            self._friends_lb.insert("end", f"{dot}{name}")

            color = {"chat": TEXT_ONLINE, "mobile": TEXT_ONLINE,
                     "away": TEXT_AWAY, "dnd": TEXT_DND}.get(state, TEXT_OFFLINE)
            idx = self._friends_lb.size() - 1
            self._friends_lb.itemconfig(idx, fg=color)

        self._set_status(True)

    # ── Friend selection ───────────────────────────────────────────────────────

    def _on_friend_select(self, _event=None):
        sel = self._friends_lb.curselection()
        if not sel:
            return
        idx = sel[0]
        if not hasattr(self, "_friend_order") or idx >= len(self._friend_order):
            return

        friend = self._friend_order[idx]
        self._selected_pid = friend["pid"]
        name = f"{friend['game_name']}#{friend.get('game_tag','')}"
        self._recipient_lbl.config(text=f"Chat: {name}", fg=TEXT_MAIN)

        if self.api:
            try:
                self._selected_cid = self.api.find_dm_cid(friend["pid"])
                self._load_chat_history()
            except Exception as e:
                self._chat_append(f"Could not load history: {e}", tag="system")

    def _load_chat_history(self):
        if not self.api or not self._selected_cid:
            return
        try:
            messages = self.api.get_messages(self._selected_cid)
            self._chat_clear()
            for m in messages[-40:]:
                sender = m.get("game_name", m.get("name", "?"))
                body   = m.get("body", "")
                # Determine if message is from us (we won't know easily, mark all)
                self._chat_append(f"{sender}: {body}\n")
        except Exception:
            pass

    # ── Messaging ──────────────────────────────────────────────────────────────

    def _send_message(self):
        if not self.api:
            self._chat_append("Not connected.", tag="system")
            return
        if not self._selected_cid:
            self._chat_append("Select a friend first.", tag="system")
            return
        msg = self._msg_var.get().strip()
        if not msg:
            return
        self._msg_var.set("")

        def _do():
            try:
                self.api.send_message(self._selected_cid, msg)
                self.after(0, lambda: self._chat_append(f"You: {msg}\n", tag="you"))
            except Exception as e:
                self.after(0, lambda: self._chat_append(f"Send error: {e}\n", tag="system"))

        threading.Thread(target=_do, daemon=True).start()

    # ── ASCII Art ──────────────────────────────────────────────────────────────

    def _on_art_select(self, _event=None):
        self._update_art_preview()

    def _update_art_preview(self):
        art = ASCII_ART.get(self._art_var.get(), "")
        self._art_preview.config(state="normal")
        self._art_preview.delete("1.0", "end")
        self._art_preview.insert("end", art)
        self._art_preview.config(state="disabled")

    def _toggle_spam(self):
        if self._spam_thread and self._spam_thread.is_alive():
            self._spam_stop.set()
            self._art_btn.config(text="⚡ SPAM ART", bg=ACCENT)
            self._spam_status.config(text="")
            return

        if not self.api:
            self._chat_append("Not connected.", tag="system")
            return
        if not self._selected_cid:
            self._chat_append("Select a friend first.", tag="system")
            return

        try:
            count = int(self._count_var.get())
            if count < 1:
                raise ValueError
        except ValueError:
            self._chat_append("Enter a valid number of times.", tag="system")
            return

        art = ASCII_ART.get(self._art_var.get(), "")
        if not art:
            return

        self._spam_stop.clear()
        self._art_btn.config(text="■ STOP", bg="#333355")
        self._spam_thread = threading.Thread(
            target=self._run_spam,
            args=(art, count),
            daemon=True,
        )
        self._spam_thread.start()

    def _run_spam(self, art: str, count: int):
        for i in range(count):
            if self._spam_stop.is_set():
                break
            try:
                self.api.send_message(self._selected_cid, art)
                self.after(0, lambda i=i, n=count: self._spam_status.config(
                    text=f"Sent {i+1}/{n}"
                ))
            except Exception as e:
                self.after(0, lambda e=e: self._spam_status.config(text=f"Error: {e}"))
                break
            time.sleep(0.05)  # 50 ms

        self.after(0, self._spam_done)

    def _spam_done(self):
        self._art_btn.config(text="⚡ SPAM ART", bg=ACCENT)
        self._spam_status.config(text="Done!")
        self.after(2500, lambda: self._spam_status.config(text=""))

    # ── Chat text helpers ──────────────────────────────────────────────────────

    def _chat_append(self, text: str, tag: str = ""):
        self._chat_text.config(state="normal")
        if tag:
            self._chat_text.insert("end", text, tag)
        else:
            self._chat_text.insert("end", text)
        self._chat_text.see("end")
        self._chat_text.config(state="disabled")

    def _chat_clear(self):
        self._chat_text.config(state="normal")
        self._chat_text.delete("1.0", "end")
        self._chat_text.config(state="disabled")

    # ── Shop window ────────────────────────────────────────────────────────────

    def _open_shop(self):
        if not self.api:
            self._chat_append("Not connected — open Riot Client first.\n", tag="system")
            return

        win = tk.Toplevel(self)
        win.title("Daily Shop")
        win.configure(bg=BG_DARK)
        win.geometry("540x420")
        win.resizable(False, False)
        win.grab_set()

        # ── header
        hdr = tk.Frame(win, bg=BG_PANEL, height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="DAILY  ", bg=BG_PANEL, fg=TEXT_DIM,
                 font=("Consolas", 13, "bold")).pack(side="left", padx=(16, 0), pady=10)
        tk.Label(hdr, text="SHOP", bg=BG_PANEL, fg=ACCENT,
                 font=("Consolas", 13, "bold")).pack(side="left", pady=10)

        self._vp_lbl = tk.Label(hdr, text="", bg=BG_PANEL, fg="#f5d442",
                                 font=("Consolas", 10, "bold"))
        self._vp_lbl.pack(side="right", padx=(0, 16))

        refresh_btn = tk.Button(
            hdr, text="⟳", bg=BG_CARD, fg=TEXT_MAIN,
            activebackground=BG_HOVER, activeforeground=TEXT_MAIN,
            relief="flat", cursor="hand2", font=("Consolas", 12),
            command=lambda: self._fetch_shop(card_grid, refresh_btn),
        )
        refresh_btn.pack(side="right", padx=(0, 4), pady=8)

        tk.Frame(win, bg=BORDER, height=1).pack(fill="x")

        # ── skin cards grid
        card_grid = tk.Frame(win, bg=BG_DARK)
        card_grid.pack(fill="both", expand=True, padx=14, pady=14)
        card_grid.columnconfigure(0, weight=1)
        card_grid.columnconfigure(1, weight=1)

        # ── wallet row
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x")
        self._wallet_lbl = tk.Label(win, text="", bg=BG_PANEL, fg=TEXT_DIM,
                                    font=("Consolas", 8))
        self._wallet_lbl.pack(fill="x", padx=16, pady=6)

        self._fetch_shop(card_grid, refresh_btn)

    def _fetch_shop(self, card_grid: tk.Frame, refresh_btn: tk.Button):
        """Fetch shop data in a background thread and populate card_grid."""
        for w in card_grid.winfo_children():
            w.destroy()

        spinner = tk.Label(card_grid, text="Fetching shop…",
                           bg=BG_DARK, fg=TEXT_DIM, font=("Consolas", 10))
        spinner.grid(row=0, column=0, columnspan=2, pady=40)
        refresh_btn.config(state="disabled")

        def _worker():
            try:
                data = self.api.get_shop()
                self.after(0, lambda: self._populate_shop(card_grid, refresh_btn, data))
            except Exception as e:
                self.after(0, lambda: self._shop_error(card_grid, refresh_btn, str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _populate_shop(self, card_grid: tk.Frame, refresh_btn: tk.Button, data: dict):
        for w in card_grid.winfo_children():
            w.destroy()

        self._vp_lbl.config(text=f"VP  {data['vp']:,}")
        name_str = f"  ·  {data['display_name']}" if data.get("display_name") else ""
        self._wallet_lbl.config(
            text=(
                f"Radianite: {data['rad']:,}  ·  "
                f"Kingdom Credits: {data['kc']:,}"
                f"{name_str}"
            )
        )

        offers = data["offers"]
        for idx, offer in enumerate(offers[:4]):
            row, col = divmod(idx, 2)
            card = tk.Frame(card_grid, bg=BG_CARD,
                            highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card_grid.rowconfigure(row, weight=1)

            tk.Label(card, text=offer["name"], bg=BG_CARD, fg=TEXT_MAIN,
                     font=("Segoe UI", 10, "bold"),
                     wraplength=210, justify="center").pack(pady=(18, 6))

            price_row = tk.Frame(card, bg=BG_CARD)
            price_row.pack(pady=(0, 16))
            tk.Label(price_row, text="VP", bg=BG_CARD, fg="#f5d442",
                     font=("Consolas", 9, "bold")).pack(side="left", padx=(0, 4))
            tk.Label(price_row, text=f"{offer['vp_cost']:,}", bg=BG_CARD,
                     fg=TEXT_MAIN, font=("Consolas", 11, "bold")).pack(side="left")

        if not offers:
            tk.Label(card_grid, text="No offers found.\nThe store may be unavailable.",
                     bg=BG_DARK, fg=TEXT_DIM, font=("Consolas", 10),
                     justify="center").grid(row=0, column=0, columnspan=2, pady=40)

        refresh_btn.config(state="normal")

    def _shop_error(self, card_grid: tk.Frame, refresh_btn: tk.Button, err: str):
        for w in card_grid.winfo_children():
            w.destroy()
        tk.Label(card_grid, text=f"Error loading shop:\n{err}",
                 bg=BG_DARK, fg=ACCENT, font=("Consolas", 9),
                 wraplength=480, justify="center").grid(
                     row=0, column=0, columnspan=2, pady=30)
        refresh_btn.config(state="normal")

    # ── Close ──────────────────────────────────────────────────────────────────

    def _on_close(self):
        self._running = False
        self._spam_stop.set()
        self.destroy()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ValASCII()
    app.mainloop()
