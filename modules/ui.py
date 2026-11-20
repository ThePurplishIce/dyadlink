from html import escape

import streamlit as st


def render_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
            --ink: #18344a;
            --muted: #526d80;
            --line: #d7e3ec;
            --surface: #ffffff;
            --blue: #244b69;
            --green: #168a78;
            --amber: #a66c18;
        }

        .stApp {
            background:
                radial-gradient(ellipse at 10% 0%, rgba(220, 239, 246, 0.76), transparent 34%),
                linear-gradient(180deg, #f4f8fb 0%, #f8fafc 52%, #f2f7fa 100%);
            color: var(--ink);
        }

        .stApp,
        .stApp p,
        .stApp span,
        .stApp label,
        .stApp li,
        .stApp a,
        .stApp button,
        .stApp input,
        .stApp textarea,
        .stApp select,
        .stApp small,
        .stApp summary,
        .stApp [role="button"],
        .stApp [data-testid="stMarkdownContainer"] *,
        .stApp [data-testid="stCaptionContainer"] *,
        .stApp [data-testid="stWidgetLabel"] *,
        .stApp [data-testid="stAlert"] *,
        .stApp [data-testid="stMetricLabel"] *,
        .stApp [data-testid="stMetricValue"] *,
        .stApp [data-testid="stMetricDelta"] *,
        .stApp div[data-baseweb="select"] *,
        .stApp svg text,
        .stApp svg tspan {
            font-weight: 700 !important;
        }

        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp [data-testid="stMarkdownContainer"] :is(h1, h2, h3, h4),
        .stApp [data-testid="stMarkdownContainer"] strong,
        .stApp [data-testid="stMarkdownContainer"] b,
        .stApp .page-title,
        .stApp .voice-title,
        .stApp .brand-name,
        .stApp .brand-cn {
            font-weight: 700 !important;
        }

        .stApp input::placeholder,
        .stApp textarea::placeholder {
            font-weight: 700 !important;
        }

        .block-container {
            max-width: 1040px;
            padding: 1.3rem 1.5rem 5.5rem;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        section[data-testid="stSidebar"] {
            background: #f8fbfd;
            border-right: 1px solid var(--line);
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 0.9rem;
            background: #ffffff;
            box-shadow: 0 6px 18px rgba(28, 64, 86, 0.06);
        }

        section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] p {
            font-size: 0.95rem;
            line-height: 1.6;
            overflow-wrap: anywhere;
        }

        h1, h2, h3, h4, p, li, label {
            color: var(--ink);
        }

        .brandline {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0 0 1.1rem;
            padding-bottom: 0.7rem;
            border-bottom: 2px solid transparent;
            border-image: linear-gradient(
                90deg, #168a78 0%, #d7e3ec 55%, transparent 100%
            ) 1;
            color: #45677f;
            font-size: 1rem;
            font-weight: 720;
            letter-spacing: 0.01em;
        }

        .brand-name {
            color: #17364e;
            font-size: 1.15rem;
            font-weight: 790;
            letter-spacing: -0.025em;
        }

        .brand-cn {
            color: #168a78;
            font-size: 1.15rem;
            font-weight: 740;
        }

        .brand-divider {
            color: #8aa0af;
        }

        .brand-page {
            color: #60788b;
            font-size: 0.92rem;
            font-weight: 600;
        }

        .page-title {
            margin: 0 0 0.55rem;
            color: #17364e;
            font-size: clamp(1.8rem, 4vw, 2.65rem);
            font-weight: 760;
            letter-spacing: -0.04em;
            line-height: 1.18;
        }

        .page-copy {
            max-width: 760px;
            margin: 0;
            color: var(--muted);
            font-size: 1.12rem;
            line-height: 1.75;
        }

        .conversation-copy {
            max-width: 820px;
            margin: 0.2rem 0 0.45rem;
            color: var(--muted);
            font-size: clamp(1.25rem, 2.2vw, 1.45rem);
            line-height: 1.7;
        }

        .scope-guide-card {
            padding: 1rem 1.1rem;
            border: 1px solid #c7dce6;
            border-left: 5px solid var(--blue);
            border-radius: 0.9rem;
            background: linear-gradient(135deg, #eaf4f7, #ffffff 76%);
            color: var(--ink);
            font-size: 1.1rem;
            line-height: 1.65;
            box-shadow: 0 8px 22px rgba(28, 64, 86, 0.08);
        }

        .crisis-card {
            padding: 1rem 1.1rem;
            border: 1px solid #f0c4c4;
            border-left: 5px solid #b03030;
            border-radius: 0.9rem;
            background: linear-gradient(135deg, #fdecec, #ffffff 76%);
            color: #6d1f1f;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.65;
            box-shadow: 0 8px 22px rgba(138, 45, 45, 0.12);
        }

        .crisis-banner {
            padding: 0.9rem 1.1rem;
            margin-bottom: 1rem;
            border: 1px solid #f0c4c4;
            border-left: 6px solid #b03030;
            border-radius: 0.9rem;
            background: #fdecec;
            color: #6d1f1f;
            font-size: 1.15rem;
            font-weight: 800;
            line-height: 1.6;
        }

        .msg-highlight {
            padding: 0.6rem 0.8rem;
            border: 2px solid #e8b93c;
            border-radius: 0.7rem;
            background: #fdf6e3;
            box-shadow: 0 0 0 4px rgba(232, 185, 60, 0.18);
        }

        :root {
            --drawer-w: min(380px, 92vw);
        }

        :root {
            --drawer-w: min(380px, 92vw);
        }

        .st-key-obs_drawer_btn {
            position: fixed;
            right: 0;
            top: 42vh;
            z-index: 1002;
            width: 2.7rem !important;
            max-width: 2.7rem !important;
            transition: right 0.28s ease;
        }

        .st-key-obs_drawer_btn button {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 10rem;
            width: 2.7rem;
            padding: 0.9rem 0.3rem;
            border: none;
            border-radius: 0.9rem 0 0 0.9rem;
            background: linear-gradient(180deg, #168a78, #127a69) !important;
            color: #ffffff !important;
            font-size: 0.95rem;
            font-weight: 800;
            letter-spacing: 0.15em;
            line-height: 1.35;
            writing-mode: vertical-rl;
            box-shadow: -8px 0 20px rgba(22, 138, 120, 0.3);
        }

        .st-key-obs_drawer_btn button:hover {
            background: linear-gradient(180deg, #127a69, #0f6a5b) !important;
        }

        .obs-open-marker {
            display: none;
        }

        .st-key-observation_drawer {
            position: fixed;
            top: 0;
            right: 0;
            height: 100dvh;
            width: var(--drawer-w);
            padding: 4.6rem 1rem 1.4rem;
            border-left: 1px solid #d7e3ec;
            background: rgba(255, 255, 255, 0.98);
            box-shadow: -16px 0 42px rgba(28, 64, 86, 0.18);
            transform: translateX(108%);
            transition: transform 0.28s ease;
            overflow-y: auto;
            z-index: 999;
        }

        body:has(.obs-open-marker) .st-key-observation_drawer {
            transform: translateX(0);
        }

        body:has(.obs-open-marker) .st-key-obs_drawer_btn {
            right: var(--drawer-w);
        }

        @media (max-width: 700px) {
            :root {
                --drawer-w: min(360px, 94vw);
            }
            .st-key-obs_drawer_btn {
                top: 30vh;
            }
            .st-key-observation_drawer {
                padding-top: 3.4rem;
            }
        }

        .obs-flag {
            display: inline-block;
            padding: 0.25rem 0.7rem;
            border: 1px solid currentColor;
            border-radius: 999px;
            font-size: 0.95rem;
            font-weight: 700;
            line-height: 1.4;
        }

        div[data-testid="stAudioInput"],
        div:has(> button[data-testid="stAudioInputActionButton"]) {
            min-height: 5rem !important;
            align-items: center !important;
            overflow: visible !important;
        }

        button[data-testid="stAudioInputActionButton"] {
            display: flex !important;
            width: 4rem !important;
            min-width: 4rem !important;
            height: 4rem !important;
            min-height: 4rem !important;
            flex: 0 0 4rem !important;
            margin: 0.2rem auto !important;
            align-items: center !important;
            justify-content: center !important;
            border: 2px solid #b9ddd4 !important;
            border-radius: 50% !important;
            background: #168a78 !important;
            color: #ffffff !important;
            box-shadow: 0 6px 18px rgba(22, 138, 120, 0.22);
        }

        button[data-testid="stAudioInputActionButton"]:hover:not(:disabled) {
            background: #126c5e !important;
        }

        button[data-testid="stAudioInputActionButton"]:disabled {
            border-color: #d8e1e7 !important;
            background: #e8eef1 !important;
            color: #738a9a !important;
            box-shadow: none;
            opacity: 1 !important;
        }

        button[data-testid="stAudioInputActionButton"] svg {
            display: block !important;
            width: 2.25rem !important;
            height: 2.25rem !important;
            min-width: 2.25rem !important;
            min-height: 2.25rem !important;
            flex-shrink: 0 !important;
            aspect-ratio: 1 / 1 !important;
        }

        button[data-testid="stAudioInputActionButton"] [data-testid="stIconMaterial"] {
            width: 2.25rem !important;
            height: 2.25rem !important;
            font-size: 2.25rem !important;
            line-height: 1 !important;
        }

        .block-container {
            max-width: 1320px;
            padding-top: 2.2rem;
        }

        div[data-testid="stChatMessage"] {
            margin: 0.6rem 0;
            padding: 0.8rem 0.95rem;
            border: 1px solid rgba(215, 227, 236, 0.72);
            border-radius: 1.15rem;
            background: rgba(255, 255, 255, 0.72);
            box-shadow: 0 4px 14px rgba(28, 64, 86, 0.05);
        }

        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            border-color: #bfe0d8;
            background: linear-gradient(135deg, #eef7f4, #ffffff 80%);
        }

        div[data-testid="stChatMessage"] p {
            font-size: 1.12rem;
            line-height: 1.75;
        }

        div[data-testid="stChatInput"] {
            border: 2px solid #bfd0dc;
            border-radius: 1.25rem;
            background: #ffffff;
            box-shadow: 0 12px 34px rgba(28, 64, 86, 0.12);
        }

        div[data-testid="stChatInput"] textarea {
            min-height: 3rem !important;
            padding: 0.4rem 0.65rem !important;
            color: #18344a !important;
            font-size: 1.12rem !important;
            line-height: 1.6 !important;
        }

        div[data-testid="stChatInput"] button {
            min-width: 3.5rem !important;
            min-height: 3.5rem !important;
            border-radius: 1rem !important;
        }

        .st-key-summary_button button {
            min-height: 5.5rem !important;
            border: 2px solid #168a78 !important;
            border-radius: 1.1rem !important;
            background: #168a78 !important;
            color: #ffffff !important;
            font-size: clamp(2rem, 4vw, 2.8rem) !important;
            font-weight: 800 !important;
            box-shadow: 0 8px 22px rgba(22, 138, 120, 0.22);
        }

        .st-key-summary_button button:hover,
        .st-key-summary_button button:focus-visible {
            background: #126c5e !important;
            border-color: #126c5e !important;
            color: #ffffff !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div > [data-testid="stVerticalBlock"]
        ) {
            border-radius: 1.1rem;
            box-shadow: 0 10px 26px rgba(28, 64, 86, 0.07);
        }

        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {
            border-radius: 0.95rem;
            background: linear-gradient(135deg, #168a78, #1a9a84) !important;
            box-shadow: 0 8px 20px rgba(22, 138, 120, 0.22);
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }

        button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover {
            background: linear-gradient(135deg, #126c5e, #157a6a) !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 26px rgba(22, 138, 120, 0.28);
        }

        div[data-testid="stMetric"] {
            min-height: 7.4rem;
            padding: 1rem 1.1rem;
            border: 1px solid var(--line);
            border-radius: 1rem;
            background: var(--surface);
            box-shadow: 0 8px 26px rgba(28, 64, 86, 0.045);
        }

        div[data-testid="stMetricValue"] {
            color: #17364e;
            font-size: clamp(1.5rem, 3vw, 2rem);
            font-weight: 740;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line);
            border-radius: 1rem;
            background: rgba(255, 255, 255, 0.78);
        }

        .history-entry {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            margin: 0.45rem 0;
            padding: 0.85rem 1.05rem;
            border: 1px solid var(--line);
            border-radius: 0.9rem;
            background: var(--surface);
        }

        .history-entry .history-meta {
            color: var(--muted);
            font-size: 0.95rem;
            font-weight: 700;
        }

        .history-entry .history-text {
            color: var(--ink);
            font-size: 1.18rem;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .history-entry.history-user {
            border-left: 5px solid #244b69;
        }

        .history-entry.history-assistant {
            border-left: 5px solid #168a78;
        }

        button, [role="button"], textarea, input, a {
            font-size: 1rem;
        }

        button {
            min-height: 3rem;
        }

        :focus-visible {
            outline: 3px solid #a66c18 !important;
            outline-offset: 3px !important;
        }

        @media (max-width: 700px) {
            .block-container {
                padding: 1rem 0.8rem 6rem;
            }

            div[data-testid="stHorizontalBlock"] {
                flex-direction: column;
                gap: 0.65rem;
            }

            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }

            .brandline {
                flex-wrap: wrap;
                font-size: 0.92rem;
            }

            button[data-testid="stAudioInputActionButton"] {
                width: 4.25rem !important;
                min-width: 4.25rem !important;
                height: 4.25rem !important;
                min-height: 4.25rem !important;
                flex-basis: 4.25rem !important;
            }

            div[data-testid="stChatInput"] button {
                min-width: 3.7rem !important;
                min-height: 3.7rem !important;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                scroll-behavior: auto !important;
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand(page_name: str) -> None:
    safe_page_name = escape(page_name)
    st.markdown(
        '<div class="brandline" role="banner">'
        '<span class="brand-name">DyadLink</span>'
        '<span class="brand-cn">伴知</span>'
        '<span class="brand-divider">/</span>'
        f'<span class="brand-page">{safe_page_name}</span>'
        "</div>",
        unsafe_allow_html=True,
    )
