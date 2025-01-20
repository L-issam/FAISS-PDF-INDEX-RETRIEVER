import streamlit as st
import base64
from pathlib import Path
from typing import Optional
from urllib.parse import quote

class PDFViewer:
    @staticmethod
    def get_pdf_js_html() -> str:
        return """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
        <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        
        async function renderPDF(base64PDF, canvasId) {
            try {
                const pdfData = atob(base64PDF);
                const loadingTask = pdfjsLib.getDocument({data: pdfData});
                const pdf = await loadingTask.promise;
                
                const canvas = document.getElementById(canvasId);
                const context = canvas.getContext('2d');
                
                // Initial page
                let pageNum = 1;
                let pageRendering = false;
                let pageNumPending = null;
                
                async function renderPage(num) {
                    pageRendering = true;
                    const page = await pdf.getPage(num);
                    
                    const viewport = page.getViewport({scale: 1.5});
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    
                    const renderContext = {
                        canvasContext: context,
                        viewport: viewport
                    };
                    
                    try {
                        await page.render(renderContext).promise;
                        pageRendering = false;
                        if (pageNumPending !== null) {
                            renderPage(pageNumPending);
                            pageNumPending = null;
                        }
                    } catch (error) {
                        console.error('Error rendering page:', error);
                    }
                    
                    document.getElementById('page_num').textContent = num;
                    document.getElementById('page_count').textContent = pdf.numPages;
                }
                
                function queueRenderPage(num) {
                    if (pageRendering) {
                        pageNumPending = num;
                    } else {
                        renderPage(num);
                    }
                }
                
                document.getElementById('prev').addEventListener('click', () => {
                    if (pageNum <= 1) return;
                    pageNum--;
                    queueRenderPage(pageNum);
                });
                
                document.getElementById('next').addEventListener('click', () => {
                    if (pageNum >= pdf.numPages) return;
                    pageNum++;
                    queueRenderPage(pageNum);
                });
                
                // Initial render
                renderPage(pageNum);
                
            } catch (error) {
                console.error('Error loading PDF:', error);
            }
        }
        </script>
        """

    @staticmethod
    def get_viewer_html(canvas_id: str) -> str:
        return f"""
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 10px;">
                <button id="prev" style="padding: 5px 10px; margin: 0 5px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 4px;">Previous</button>
                <span>Page: <span id="page_num"></span> / <span id="page_count"></span></span>
                <button id="next" style="padding: 5px 10px; margin: 0 5px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 4px;">Next</button>
            </div>
            <canvas id="{canvas_id}" style="max-width: 100%; height: auto;"></canvas>
        </div>
        """

    @staticmethod
    def display_pdf(pdf_path: Optional[Path], page: int = 1, highlight_text: str = None) -> None:
        if pdf_path is None:
            st.info("Select a PDF from the sidebar to view it here.")
            return

        try:
            with open(pdf_path, "rb") as f:
                try:
                    header = f.read(4)
                    if header[:4] != b'%PDF':
                        st.error(f"Invalid PDF format: {pdf_path.name}")
                        return
                    
                    f.seek(0)
                    pdf_content = f.read()
                    base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
                    
                    st.markdown("""
                        <style>
                        .pdf-container {
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            width: 100%;
                            height: 800px;
                            background: white;
                            padding: 20px;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }
                        iframe {
                            width: 100%;
                            height: calc(100% - 20px);
                            border: none;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    # Construire l'URL avec le paramètre de page
                    pdf_url = f"data:application/pdf;base64,{base64_pdf}#page={page}"
                    
                    pdf_display = f"""
                    <div class="pdf-container">
                        <iframe 
                            src="{pdf_url}"
                            type="application/pdf"
                            scrolling="auto">
                        </iframe>
                    </div>
                    """
                    st.markdown(pdf_display, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error reading PDF {pdf_path.name}: {str(e)}")
                    
        except Exception as e:
            st.error(f"Error opening file {pdf_path}: {str(e)}")