# pyrefly: ignore [missing-import]
import streamlit as st

def render_html_button(label: str, url: str = "#", variant: str = "primary", use_container_width: bool = False, key: str = "") -> None:
    """
    Renders an HTML-based button styled using the theme's SaaS button classes.
    Excellent for external links, anchor scrolling, or standard actions.
    Variants: 'primary', 'accent', 'secondary'
    """
    variant_class = f"saas-btn-{variant}"
    width_style = "width: 100%;" if use_container_width else ""
    
    st.markdown(
        f'<a href="{url}" class="saas-btn {variant_class}" style="{width_style}" id="{key}">{label}</a>',
        unsafe_allow_html=True
    )

def render_streamlit_button(label: str, key: str, variant: str = "primary", use_container_width: bool = True) -> bool:
    """
    Renders a standard Streamlit button styled matching the design system guidelines.
    Streamlit natively supports primary (type="primary") and secondary (type="secondary").
    """
    btn_type = "primary" if variant == "primary" or variant == "accent" else "secondary"
    return st.button(label, key=key, type=btn_type, use_container_width=use_container_width)
