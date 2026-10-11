"""V2-E shared chart renderer: descriptive titles + explicit expand + download.

Every Streamlit/Plotly graphic (league, team, comparison, legends) should call
render_chart, so users can always open an enlarged interactive version.
Never executes chart HTML through unsafe Markdown in the main page.
"""
from __future__ import annotations
from copy import deepcopy
import re

PLOT_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'responsive': True,
    'scrollZoom': False,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'toImageButtonOptions': {'format': 'png', 'scale': 2},
}


def chart_title(fig, override=None):
    explicit = str(override or '').strip()
    in_figure = str(fig.layout.title.text or '').strip()
    title = explicit or in_figure
    if not title or title.lower() in {'untitled', 'none', 'chart', 'figure'}:
        raise ValueError('Every chart must have a meaningful sports-analytics title')
    # Plotly figure title can have inline styling; header shows plain language.
    return re.sub(r'<[^>]+>', '', title)


def expanded_chart_html(fig, title):
    """Self-contained HTML serves as full-browser-tab fallback/offline export."""
    copy = deepcopy(fig)
    copy.update_layout(title_text=title, autosize=True, height=None,
                       margin=dict(l=65, r=50, t=75, b=70))
    return copy.to_html(full_html=True, include_plotlyjs=True,
                        config=PLOT_CONFIG)


def render_chart(fig, *, key: str, title: str | None = None,
                 height: int | None = None, context: str | None = None):
    import streamlit as st
    if fig is None:
        st.info('No observations available for this chart with the selected filters.')
        return
    caption = chart_title(fig, title)
    if not key or not str(key).strip():
        raise ValueError('Chart key is required and must be stable')
    slug = re.sub(r'[^a-zA-Z0-9_-]+', '_', str(key))[:130]
    if height:
        fig.update_layout(height=height)
    left, right = st.columns([6, 1.7], vertical_alignment='center')
    with left:
        st.markdown(f'**📊 {caption}**')
    with right:
        expand = st.button('⛶ Full screen', key=f'expand_{slug}',
                           help=f'Open a large interactive view: {caption}',
                           use_container_width=True)
    st.plotly_chart(fig, use_container_width=True, key=f'visual_{slug}',
                    config=PLOT_CONFIG)
    if context:
        st.caption(context)
    if expand:
        @st.dialog(f'Expanded: {caption}', width='large')
        def _open_fullscreen():
            st.markdown('''<style>
            [data-testid="stDialog"] [role="dialog"] {
              width:96vw!important;max-width:96vw!important;
              max-height:94vh!important;overflow-y:auto!important;
              background:#0C172A!important;
            }
            </style>''', unsafe_allow_html=True)
            big = deepcopy(fig)
            big.update_layout(height=650, autosize=True, title_text=caption,
                              margin=dict(l=45,r=30,t=80,b=55))
            st.plotly_chart(big, use_container_width=True,
                            key=f'expanded_{slug}', config=PLOT_CONFIG)
            st.caption('Interactive expanded view · pan, zoom and download image using the chart toolbar.')
            st.download_button('⬇ Download interactive full-screen HTML',
                               data=expanded_chart_html(fig, caption),
                               file_name=f'IPL360_{slug}.html', mime='text/html',
                               key=f'html_{slug}')
        _open_fullscreen()
