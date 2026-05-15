# components/SortableRow.py
import gradio as gr


class SortableRow:
    def __init__(self, row_id, options):
        self.id = row_id
        with gr.Row(elem_classes="sortable-row") as self.row:
            self.handle = gr.HTML('<div class="handle">☰</div>')
            self.dropdown = gr.Dropdown(options, label=f"选项 {row_id}")
            self.delete_btn = gr.Button("❌", elem_classes="delete-btn")

            # 删除事件
            self.delete_btn.click(fn=lambda: None, inputs=None, outputs=None)
