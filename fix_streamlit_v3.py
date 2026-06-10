"""
Fix script for streamlit_app_v3.py — addresses deprecation warnings and stability issues.
"""
import re

filepath = "streamlit_app_v3.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Count occurrences before
before = content.count("use_container_width")
print(f"Found {before} occurrences of 'use_container_width'")

# Fix 1: Remove use_container_width=True from st.dataframe calls
# Pattern: st.dataframe(..., use_container_width=True, ...)
content = re.sub(
    r'st\.dataframe\(([^)]*?),\s*use_container_width=True,\s*([^)]*?)\)',
    r'st.dataframe(\1, \2)',
    content
)

# Fix 2: Remove use_container_width=True from st.altair_chart calls
# Pattern: st.altair_chart(..., use_container_width=True)
content = re.sub(
    r'st\.altair_chart\(([^)]*?),\s*use_container_width=True\s*\)',
    r'st.altair_chart(\1)',
    content
)

# Verify
after = content.count("use_container_width")
print(f"After fix: {after} occurrences remain")

# Fix 3: Improve auto-refresh — use st_autorefresh instead of time.sleep + st.rerun
# This is more reliable and avoids blocking the UI
if "time.sleep(3)" in content and "st.rerun()" in content:
    old_refresh = """# =============================================================================
# AUTO-REFRESH MECHANISM
# =============================================================================
if st.session_state.live_mode:
    time.sleep(3)
    st.rerun()"""

    new_refresh = """# =============================================================================
# AUTO-REFRESH MECHANISM — using streamlit-autorefresh for reliability
# =============================================================================
if st.session_state.live_mode:
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=3000, limit=None, key="auto_refresh")
    except ImportError:
        # Fallback: manual refresh button if autorefresh not installed
        st.sidebar.button("🔄 Refresh Now", on_click=lambda: st.rerun(), use_container_width=True)
        st.sidebar.caption("Install `streamlit-autorefresh` for automatic refresh")
else:
    # Show manual refresh button when live mode is off
    if st.sidebar.button("🔄 Refresh Now", key="manual_refresh"):
        st.rerun()"""

    content = content.replace(old_refresh, new_refresh)
    print("Replaced auto-refresh mechanism")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixes applied successfully!")
