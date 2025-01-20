import streamlit as st
from pathlib import Path
from typing import Optional

class Sidebar:
    def __init__(self, sources_dir: Path):
        self.sources_dir = sources_dir

    def render(self, processed_pdfs: set) -> Optional[Path]:
        with st.sidebar:
            st.markdown("📑 Processed Documents")
            st.markdown("### Available PDFs")
            
            # Utiliser un container pour éviter le rechargement
            container = st.container()
            
            # Stocker la sélection dans session_state
            if 'selected_pdf' not in st.session_state:
                st.session_state.selected_pdf = None
            
            for pdf in sorted(processed_pdfs):
                pdf_path = self.sources_dir / pdf
                # Utiliser un bouton stylisé comme un lien
                if container.button(
                    f"📄 {pdf}",
                    key=f"btn_{pdf}",
                    help="Click to view this PDF",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.selected_pdf = pdf_path
            
            return st.session_state.selected_pdf